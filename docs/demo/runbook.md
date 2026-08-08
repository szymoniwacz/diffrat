# Diffrat 5-minute demo runbook

Presenter script for a short **review-triage** demo (Sam / PR triage pitch).
Use a real git diff plus the committed sample report when you want a stable
Focus/Risk story without inventing a scenario live.

**Do not lead with** `diffrat review --check` or private AI-workflow setup
(`./scripts/setup-ai-workflow.sh`, `.ai-template/`, Cursor Automations). Those
are maintainer paths. This demo is install → review → triage → optional gate.

## What you need

- Python 3.11+ and git on PATH
- About five minutes
- Either:
  - a disposable feature branch with a small messy diff, or
  - the static sample at [`sample-brief-report.txt`](sample-brief-report.txt)
    (clearly labeled SAMPLE) if the live branch is clean or awkward

## Minute 0–1: Install

```bash
pip install diffrat
diffrat --version
```

From a clone (optional):

```bash
pip install -e .
diffrat --version
```

Say aloud: Diffrat is a local CLI. Offline by default. It ranks what to look at
first — it does not auto-approve PRs.

## Minute 1–2: Prepare a real diff

`diffrat review` needs a **non-empty** diff. On clean `main` with
`--base main`, exit code `2` is expected.

Quick options:

1. Checkout a feature branch that already differs from `main`, or
2. Make a few local edits (auth-ish path + a script + a doc) and leave them
   unstaged, or
3. Fall back to the committed sample report and narrate from that text

```bash
# Prefer a real branch when you have one
git checkout -b demo/messy-review   # optional local-only branch
# ... edit a couple of files, leave unstaged or commit a WIP subject ...
```

## Minute 2–4: Recommended commands

Run triage-first (omit hunk noise):

```bash
diffrat review --base main --brief
```

Optional JSON for tooling demos:

```bash
diffrat review --base main --brief --json
```

Point at **Review order**, then **Focus / Risk**. Call out product value with
hints such as `possible_secret`, `dangerous_call`, `wip_commits`, and
`mixed_concerns`. If the live branch is quiet, open
[`sample-brief-report.txt`](sample-brief-report.txt) and walk the same
sections — say clearly that it is a **sample**, not live output.

Then show a scriptable gate:

```bash
diffrat review --base main --fail-on=possible_secret,dangerous_call
```

Exit `4` means at least one requested hint code matched. That is a triage
signal for humans or CI — not an approval.

## Minute 4–5: What to say aloud

1. **Problem:** Reviewers drown in unordered diffs; risky lines hide in noise.
2. **Move:** `diffrat review --base main --brief` → Review order + Focus/Risk.
3. **Gate:** `--fail-on=…` fails the command when those codes appear.
4. **Boundary:** Diffrat helps you decide where to look. A human still owns
   approve/merge. Do not pitch auto-approve.

If someone asks about `--check` or the private `.ai/` workflow, defer: useful
for maintainers, not the opening demo path.

## Checklist (presenter)

- [ ] Installed / version shown
- [ ] Non-empty diff or sample report ready
- [ ] Ran `--brief` (or walked the sample)
- [ ] Named Review order + at least one Focus/Risk finding
- [ ] Showed or described `--fail-on`
- [ ] Closed on triage, not auto-approve
- [ ] Did **not** open with `--check` or AI-workflow setup
