# Reproducing approach A

Approach A needs no private software. The steps below describe how it was run. They are not packaged as a script.

1. Check out the project at its audited commit, with its dependencies installed.

   | Project | Repository | Audited commit | Fixed commit |
   |---|---|---|---|
   | ONCHAINID | https://github.com/T-REX-Network/ONCHAINID | `d2096509` | `4fda2052` |
   | GTE | https://github.com/code-423n4/2025-08-gte-perps | `f43e1ee` | none public |
   | Promis | https://github.com/promis-finance/promis-contracts | `4cd2d431` | `63ca7351` |

2. Fill the values in braces of [`prompt-plain-model.md`](prompt-plain-model.md) for the project and save the result as `prompt.txt`.
3. Run the model in the checkout, with no network access and no web tools:

   ```
   claude -p --model claude-opus-5-5 --effort medium \
     --tools "Bash Read Write Edit Glob Grep Agent" \
     --disallowedTools WebSearch WebFetch \
     --permission-mode acceptEdits < prompt.txt
   ```

4. Score each reported test with the judge. It expects the project checkout at `targets/<project>` beside `ground-truth/`:

   ```
   python3 method/judge.py <project> <workspace> <test-path> --attribute
   ```

   The judge applies where a fixed commit exists. GTE findings were matched by reading.

The full commit hashes are in [`ground-truth/`](../ground-truth/). The model version, tool versions and the run settings are in section 9 of the paper.
