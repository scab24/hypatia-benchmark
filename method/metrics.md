# Metrics

The plan of what to measure, written before the first counted run and kept as written. It calls an approach an "arm" and a project a "target". The paper states which of these were reported and which planned checks were not done (section 7).

Every metric is reported per target and per arm. Nothing is averaged over targets
without the per-target rows next to it. No confidence intervals and no significance
claims: the sample is a handful of targets.

## Headline (the three results)

| # | Metric | Definition |
|---|---|---|
| 1 | Severe findings found | Official Critical and High findings matched by a reported finding that passes the judge. Given as found in at least one of 3 runs, and found in all 3 runs. |
| 2 | Precision | Reported findings that pass the judge, divided by all reported findings. The rest are false reports. |
| 3 | Own contribution | Official findings an arm found that the arm below it did not: B over A (the process), C over B (the code map). |

## Secondary

| # | Metric | Definition |
|---|---|---|
| 4 | Medium findings found | Same as 1, for official Medium findings that have a public fix and a harm a test can show. |
| 5 | Extra valid findings | Reported findings that pass the judge and match nothing in the official list. Counted apart, each one read by a human. |
| 6 | Severity agreement | Share of matched findings whose reported severity equals the official one, and share within one level. |
| 7 | Consistency | Share of findings found in 3 of 3 runs, among those found at least once. |

## Cost

| # | Metric | Definition |
|---|---|---|
| 8 | Tokens and wall time | Per run, as measured. |
| 9 | Tokens per valid finding | Tokens of the run divided by its findings that pass the judge. |
| 10 | Findings against tokens spent | Cumulative valid findings at 0.5, 1, 2 and 3 million tokens, taken from the transcript position where each finding was first recorded. |

## Why (process and failure analysis)

| # | Metric | Definition |
|---|---|---|
| 11 | Where a missed finding was lost | For every official finding an arm missed: out of scope, code not visited, visited but no hypothesis, hypothesis dropped, not proven. Mechanical (`hypatia missed`) for arms B and C; read by hand from the transcript for arm A, and labelled as such. |
| 12 | Coverage | Arms B and C only: functions examined, call pairs decided, and how each closure is backed (test, cited guard, reasoning only). |

## Target descriptors (not results)

Lines of code in scope without comments and blanks, state-changing functions, call
pairs that share state, number of official findings by severity, dates of the audited
commit and of the fixed version.

## Checks on the measurement itself

- A human reads a sample of the judge's verdicts (every severe match, and a sample of the rest).
- The judge is run on a planted bug (must pass) and on a correct test of a non-bug (must fail).
- A memory probe per target: the bare model is asked for the findings without the code.
- Every transcript is checked for network use and for reads outside the run folder.

## Metric set agreed on 2026-11-17 (supersedes the lists above where they differ)

Chosen to match what Anthropic's security evaluations report (see
`report/RELATED-WORK.md`, "Metrics reported by comparable evaluations"), adapted to this
benchmark. Approved by the project owner.

| Metric | Follows | How we compute it |
|---|---|---|
| Success decided by an executable test, not by opinion | Anthropic smart-contracts post | judge: the test passes on the audited commit and fails on the fixed one; matches made by reading are flagged |
| Official findings found, by severity | targets exploited (same post) | strict and lenient counts per arm |
| Clean versus contaminated targets | knowledge-cutoff split (same post) | ONCHAINID and Promis clean; GTE contaminated, with the memory probe |
| Found in k of n repetitions | Best@N (same post) | ONCHAINID, n = 3; no confidence interval at n = 3 |
| Cap per run, stated | 60-minute, 2-hour and 300-turn caps in Anthropic's evaluations | plain arm: no cap stated; Hypatia: max iterations (100 in the first runs, 40 in the corrected ones) |
| Tokens per valid finding | median tokens per successful exploit (same post) | output tokens of the run divided by valid findings |
| Dollar-equivalent per run and per official finding | cost per run and per vulnerable contract (same post) | reported as data; this benchmark runs on a subscription |
| Findings outside the official report, validated | zero-days (same post) | `scoring/*/EXTRA-FINDINGS.md`; valid only after an auditor's decision |
| Severity agreement | Mythos Preview assessment | reported severity against the official one |
| Wall-clock minutes per run, model and tool time apart | A1, CVE-Bench, Heimdallr (Anthropic reports caps, not mean times) | main effort measure here, because of the subscription; runs made while the machine was busy are marked not comparable |
| Precision: reported findings that are real | Heimdallr, AIxCC accuracy multiplier (not in Anthropic's posts) | valid findings (official or validated extra) over reported |
| Questions decided, questions left open (Hypatia arms) | no external source: our own, labelled as such | from the what-if plan at closure |

Not used: time to first valid finding and findings per hour (no source uses them).
