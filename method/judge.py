#!/usr/bin/env python3
"""Differential judge: does a reported test show harm on the audited code and stop
showing it on the fixed code?

For one test of one run the judge:

1. builds a clean copy of the audited commit and a clean copy of the fixed commit
   (git archive + the installed dependencies), never the run's own workspace;
2. copies into both the test and the files it imports among those the run ADDED to its
   workspace (untracked files); tracked files the run modified are never copied;
3. runs the test in both copies and classifies each outcome:
     pass            the test passed
     assert_fail     the test ran and one of its tests failed
     setup_fail      setUp() failed: the test never reached its claim
     compile_fail    the copy did not compile with the added files
     no_test         no test matched
4. verdict:
     counts          pass on audited, assert_fail on fixed
     not_shown       not pass on audited
     not_fixed       pass on audited and pass on fixed (not one of the fixed findings,
                     or the test proves nothing)
     human           pass on audited, but the fixed copy failed to compile or failed
                     in setUp: the failure is not evidence, and the finding is left to reading. With
                     --attribute the verdict becomes `counts` (basis: fix_commit) when
                     one official fix commit alone turns the test from pass to assert_fail
5. attribution (optional, --attribute): for every official finding with a fix commit,
   the fix is merged alone onto the audited commit and the test is run on the result;
   when that merge conflicts, the test is run just before and at the fix in the project
   history instead. The finding whose fix turns the test from pass to assert_fail is
   the match. A fix that changes the signature the test calls cannot be matched this
   way: the test stops compiling, the verdict stays `human`.

Usage:
  judge.py <target> <workspace> <test-path> [--match-test NAME] [--attribute] [--keep]
Prints one JSON object.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BENCH = Path(__file__).resolve().parents[1]
DEPS = {"onchainid": ["dependencies"], "vana": ["node_modules", "lib/forge-std"], "stablegold": [], "gte": ["lib"], "promis": ["node_modules"]}
IGNORED_PREFIXES = (".hypatia/", ".codegraph/", "out/", "cache/", "cache_forge/", "crytic-export/", "broadcast/")
TIMEOUT = 1800
PROBE_STAGE = "test/.hypatia-probe-bench"


def run(cmd: list[str], cwd: Path, timeout: int = TIMEOUT, env: dict | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    return proc.returncode, proc.stdout + proc.stderr


def added_files(workspace: Path) -> tuple[list[str], list[str]]:
    """Files the run added (untracked) and tracked files it changed."""
    _, out = run(["git", "status", "--porcelain", "--untracked-files=all"], workspace)
    added, changed = [], []
    for line in out.splitlines():
        code, path = line[:2], line[3:].strip().strip('"')
        if path.startswith(IGNORED_PREFIXES):
            continue
        (added if code == "??" else changed).append(path)
    return added, changed


def closure(workspace: Path, test: str, added: list[str]) -> list[str]:
    """The test plus the added files it imports, directly or not. A broken file the
    run added elsewhere must not stop an unrelated test from compiling."""
    pool, keep, todo = set(added), [], [test]
    while todo:
        rel = todo.pop()
        if rel in keep or rel not in pool:
            continue
        keep.append(rel)
        try:
            text = (workspace / rel).read_text(errors="replace")
        except OSError:
            continue
        for target in re.findall(r'import\s[^;]*?["\']([^"\']+)["\']\s*;', text):
            for candidate in ((Path(rel).parent / target), Path(target)):
                norm = Path(*[part for part in candidate.parts if part != "."]).as_posix()
                parts: list[str] = []
                for part in norm.split("/"):
                    if part == ".." and parts:
                        parts.pop()
                    else:
                        parts.append(part)
                todo.append("/".join(parts))
    return keep


def clean_copy(target: str, commit: str, dest: Path) -> None:
    src = BENCH / "targets" / target
    dest.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(src), "archive", commit], capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
    for dep in DEPS[target]:
        (dest / dep).parent.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(dest / dep, ignore_errors=True)  # a submodule leaves an empty folder in the archive
        shutil.copytree(src / dep, dest / dep, symlinks=True)
    if target == "stablegold":
        (dest / "foundry.toml").write_text('[profile.default]\nsrc = "contracts"\nout = "out"\nlibs = []\nsolc_version = "0.8.30"\n')
        shutil.copytree(BENCH / "targets/onchainid/dependencies/forge-std-v1.14.0", dest / "lib/forge-std")
        (dest / "remappings.txt").write_text("forge-std/=lib/forge-std/src/\n")
    if target == "promis":
        # The same files the harness adds to a Promis workspace.
        (dest / "foundry.toml").write_text('[profile.default]\nsrc = "contracts"\nout = "out"\nlibs = ["node_modules", "lib"]\n'
                                           'solc_version = "0.8.29"\nevm_version = "cancun"\noptimizer = true\noptimizer_runs = 1000\n')
        shutil.copytree(BENCH / "targets/onchainid/dependencies/forge-std-v1.14.0", dest / "lib/forge-std")
        (dest / "remappings.txt").write_text(
            "@openzeppelin/contracts/=node_modules/@openzeppelin/contracts/\n"
            "@openzeppelin/contracts-upgradeable/=node_modules/@openzeppelin/contracts-upgradeable/\n"
            "@morpho-org/=node_modules/@morpho-org/\n@cryptoalgebra/=node_modules/@cryptoalgebra/\n"
            "@redstone-finance/=node_modules/@redstone-finance/\nforge-std/=lib/forge-std/src/\n")


def classify(code: int, output: str) -> str:
    if code == 124:
        return "timeout"
    if re.search(r"Compiler run failed|Error \(\d+\)|Compilation failed", output):
        return "compile_fail"
    if re.search(r"No tests (found|match)", output):
        return "no_test"
    if re.search(r"\[FAIL[^\]]*\]\s+setUp\(\)", output):
        return "setup_fail"
    summary = re.search(r"(\d+) tests? passed, (\d+) failed", output)
    if summary:
        passed, failed = int(summary.group(1)), int(summary.group(2))
        if failed:
            return "assert_fail"
        return "pass" if passed else "no_test"
    return "pass" if code == 0 and "[PASS]" in output else "unknown"


def run_test(target: str, commit: str, workspace: Path, files: list[str], test: str, match: str | None,
             root: Path, label: str) -> dict:
    copy = root / label
    clean_copy(target, commit, copy)
    for rel in files:
        dest, source = (rel, workspace / rel) if isinstance(rel, str) else rel
        (copy / dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, copy / dest)
    cmd = ["forge", "test", "--match-path", test]
    if match:
        cmd += ["--match-test", match]
    env = None
    if not test.startswith(("test/", "tests/")):
        # Forge only looks for tests in its test directory: point it at the folder
        # the run put this test in (what the run itself had to do to execute it).
        env = dict(os.environ, FOUNDRY_TEST=str(Path(test).parent))
    code, output = run(cmd, copy, env=env)
    fails = re.findall(r"\[FAIL[^\n]*", output)[:3]
    return {"commit": commit[:10], "outcome": classify(code, output), "exit": code, "fail_lines": [f[:240] for f in fails]}


def verdict(audited: str, fixed: str) -> str:
    if audited != "pass":
        return "not_shown"
    return {"assert_fail": "counts", "pass": "not_fixed"}.get(fixed, "human")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("workspace", type=Path)
    ap.add_argument("test")
    ap.add_argument("--match-test")
    ap.add_argument("--attribute", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--poc-root", type=Path, help="Hypatia approaches: folder holding the probe sources (the hunt's poc/)")
    ap.add_argument("--poc-files", help="Hypatia approaches: comma-separated probe files of this issue, relative to --poc-root")
    args = ap.parse_args()

    truth = json.loads((BENCH / "ground-truth" / f"{args.target}.json").read_text())
    workspace = args.workspace.resolve()
    added, changed = added_files(workspace)
    result: dict = {"target": args.target, "test": args.test, "match_test": args.match_test,
                    "added_files": len(added), "changed_tracked_files": changed}
    if args.poc_root:
        # Hypatia keeps probe sources in the hunt's poc/ and stages them into the project
        # test directory for a run; the judge stages the same files the same way.
        names = [n for n in (args.poc_files or "").split(",") if n]
        added = [(f"{PROBE_STAGE}/{name}", args.poc_root.resolve() / name) for name in names]
        result["copied_files"] = [dest for dest, _ in added]
    else:
        if args.test not in added:
            result.update(verdict="invalid", reason="the test file is not a file the run added")
            print(json.dumps(result, indent=2))
            return 0
        added = closure(workspace, args.test, added)
        result["copied_files"] = added
    root = Path(tempfile.mkdtemp(prefix="bench-judge-"))
    try:
        audited = run_test(args.target, truth["audited_commit"], workspace, added, args.test, args.match_test, root, "audited")
        fixed = run_test(args.target, truth["fixed_commit"], workspace, added, args.test, args.match_test, root, "fixed")
        result.update(audited=audited, fixed=fixed, verdict=verdict(audited["outcome"], fixed["outcome"]))
        if changed:
            result["note"] = "the run modified tracked files; they are NOT copied, the clean code is judged"
        if args.attribute and audited["outcome"] == "pass":
            matches, seen = [], {}
            src = BENCH / "targets" / args.target
            for finding in truth["findings"]:
                commit = finding.get("fix_commit")
                if not commit:
                    continue
                if commit not in seen:
                    # First choice: this fix alone, merged onto the audited commit, so that
                    # unrelated later changes cannot break the test. If it does not merge
                    # cleanly, fall back to the project history just before and at the fix.
                    merged = subprocess.run(["git", "-C", str(src), "merge-tree", "--write-tree", "--merge-base",
                                             commit + "^", truth["audited_commit"], commit], capture_output=True, text=True)
                    if merged.returncode == 0:
                        tree = merged.stdout.split()[0]
                        after = run_test(args.target, tree, workspace, added, args.test, args.match_test, root, f"alone-{commit}")
                        seen[commit] = ("alone", "pass", after["outcome"])
                        if not args.keep:
                            shutil.rmtree(root / f"alone-{commit}", ignore_errors=True)
                    else:
                        before = run_test(args.target, commit + "^", workspace, added, args.test, args.match_test, root, f"pre-{commit}")
                        after = run_test(args.target, commit, workspace, added, args.test, args.match_test, root, f"at-{commit}")
                        seen[commit] = ("history", before["outcome"], after["outcome"])
                        if not args.keep:
                            shutil.rmtree(root / f"pre-{commit}", ignore_errors=True)
                            shutil.rmtree(root / f"at-{commit}", ignore_errors=True)
                _method, before_o, after_o = seen[commit]
                if before_o == "pass" and after_o == "assert_fail":
                    matches.append(finding["id"])
            result["attribution"] = {"flipped_by": matches, "per_commit": {k: list(v) for k, v in seen.items()}}
            if matches and result["verdict"] == "human":
                # The final fixed version no longer compiles or sets up with this test, but
                # one fix commit, taken alone, turns it from passing to failing.
                result["verdict"] = "counts"
                result["verdict_basis"] = "fix_commit"
    finally:
        if args.keep:
            result["kept"] = str(root)
        else:
            shutil.rmtree(root, ignore_errors=True)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
