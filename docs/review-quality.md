# Review quality pillars

Every `diffrat review` report answers three review questions on the diff:

1. **Understand in seconds** — can the next developer or AI grasp the change quickly?
2. **One thing well** — is the scope focused?
3. **Safe to change in six months** — are tests, boundaries, and fragile patterns in good shape?

The CLI surfaces this as a **Review quality** section in text output (after
**Summary**, before **Files**) and as additive `review_quality` in `--json`.
Both are built from existing Focus/Risk hints — no LLM, no whole-repo scan.

## Pillar status

Each pillar rolls up to one of three statuses:

| Status | Meaning |
|---|---|
| `ok` | No `warn` or `risk` hints mapped to this pillar |
| `warn` | At least one `warn` hint, and no `risk` hints |
| `risk` | At least one `risk` hint |

Rollup rules (`src/diffrat/review_quality.py`):

- `info` hints are ignored for pillar status.
- A pillar with any `risk` hint becomes `risk` (even if `warn` hints also match).
- A pillar with only `warn` hints becomes `warn`.
- Unmapped hint codes default to the **Safe to change in six months** pillar.

Text output lists each pillar on one line. When status is not `ok`, matched hint
codes appear in parentheses:

```text
Review quality
--------------
- Understand in seconds: ok
- One thing well: warn (mixed_concerns)
- Safe to change in six months: risk (possible_secret, source_without_tests)
```

## JSON shape

With `--json`, `review_quality.pillars[]` contains one object per pillar:

```json
{
  "review_quality": {
    "pillars": [
      {
        "id": "understand",
        "label": "Understand in seconds",
        "status": "ok",
        "codes": []
      },
      {
        "id": "focused",
        "label": "One thing well",
        "status": "warn",
        "codes": ["mixed_concerns"]
      },
      {
        "id": "maintainable",
        "label": "Safe to change in six months",
        "status": "risk",
        "codes": ["possible_secret", "source_without_tests"]
      }
    ]
  }
}
```

`schema_version` stays `"1"`. The existing `focus_risk` array is unchanged.

## Code → pillar mapping

Every built-in hint code in `HINT_SEVERITY_REGISTRY` maps to exactly one pillar.
Unknown codes fall back to **Safe to change in six months**.

### Understand in seconds (`understand`)

| Code | Default severity | Trigger (summary) |
|---|---|---|
| `large_diff` | warn | Total diff exceeds line threshold |
| `large_single_file` | warn | One file dominates the diff |
| `deletions_heavy` | warn | Deletions outweigh additions |
| `rename_or_move` | warn | Rename/copy detected |
| `generated_file_touched` | warn | Generated artifact path touched |
| `regex_typo` | warn | Validator typo pattern in diff |
| `docs_touched` | info | Documentation files changed |
| `long_added_hunk` | warn | Single hunk adds ≥ 40 lines |
| `cli_flag_without_help` | warn | `add_argument` without `help=` in CLI entry file |

### One thing well (`focused`)

| Code | Default severity | Trigger (summary) |
|---|---|---|
| `tests_only` | warn | Diff contains only test files |
| `many_commits` | warn | Many commits since base |
| `wip_commits` | warn | WIP-style commit messages |
| `mixed_concerns` | warn | Multiple unrelated change themes |

### Safe to change in six months (`maintainable`)

| Code | Default severity | Trigger (summary) |
|---|---|---|
| `security_sensitive_paths` | risk | Security-sensitive path touched |
| `ci_workflow_paths` | risk | CI/workflow path touched |
| `possible_secret` | risk | Possible secret in added lines |
| `dangerous_call` | risk | Dangerous API call pattern |
| `config_or_deps` | warn | Config or dependency file changed |
| `suspicious_constant_change` | warn | Suspicious constant modification |
| `tests_touched` | warn | Test files changed |
| `source_without_tests` | warn | Source changed without tests in diff |
| `source_heavy_without_tests` | warn | ≥ 40 source additions, ≥ 75% of total, no tests |
| `ci_without_tests` | warn | CI changed without tests in diff |
| `missing_test_file` | warn | Expected test file missing |
| `lockfile_without_manifest` | warn | Lockfile without manifest |
| `manifest_without_lockfile` | warn | Manifest without lockfile |
| `debug_leftover` | warn | Debug statement in added lines |
| `broad_exception` | warn | Overly broad exception handler |
| `hardcoded_url_or_ip` | warn | Hardcoded URL or IP in added lines |

Severity defaults come from `src/diffrat/scoring.py`. Pillar mapping lives in
`src/diffrat/review_quality.py` (`CODE_TO_PILLAR`).

## Diff-scoped hint details

These hints inspect diff content only (no whole-repo scan).

### `long_added_hunk`

Fires when a single unified-diff hunk adds **40 or more** lines. Suggests
splitting large hunks for reviewability.

### `source_heavy_without_tests`

Fires when:

- No test files appear in the diff, **and**
- Source additions total **≥ 40 lines**, **and**
- Source additions are **≥ 75%** of all additions in the diff.

### `cli_flag_without_help`

Fires on added `add_argument(...)` calls in CLI entry files (`__main__.py`,
`*_cli.py`, or paths under `cli/`) that lack `help=` text. Calls with
`action="version"` are excluded.

## Related output

- **Focus / Risk** — full hint list with messages and optional path/line
  (`focus_risk` in JSON). See [README](../README.md#focus--risk-categories-and-ordering).
- **Review order** — up to five highest `risk_score` files for triage.
