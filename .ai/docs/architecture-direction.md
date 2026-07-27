# Architecture Direction

## Purpose

Describe the intended architecture before implementation starts.

This file should not contain final code decisions too early.
It should describe direction, constraints, and boundaries.

## System shape

Local **Python CLI** (`numbat`) invoked from a git repository working copy.
No long-running server in v1. No web UI.

```txt
Developer/Reviewer
       │
       ▼
  numbat CLI (argparse/click TBD at scaffold)
       │
       ├── Git adapter ──► local git (diff, log, branch metadata)
       │
       ├── Diff parser ──► normalized change model
       │
       ├── Analysis backend ──► report sections (heuristics first)
       │
       └── Output renderer ──► terminal | JSON (--json)
```

## Main boundaries

| Component | Responsibility | Must not |
|---|---|---|
| CLI layer | Args, exit codes, stdout/stderr contract | Embed analysis rules |
| Git adapter | Invoke/read git; handle missing repo | Parse diff semantics |
| Diff parser | Normalize hunks, files, stats | Call LLM or network |
| Analysis backend | Produce review signals and summaries | Write to git or network (v1 static) |
| Output renderer | Format report for human or JSON | Change analysis results |

## Design principles

- **Local-first:** default path uses only local git and deterministic logic
- **Diff-scoped:** never scan the full tree in v1
- **Explicit I/O contract:** stable `--json` schema once introduced; semver for breaking changes
- **Fail clearly:** missing git repo, empty diff, invalid ref → non-zero exit + message
- **Small steps:** ship diff ingestion before optional LLM
- **Assist, not decide:** output guides review; never auto-approve or merge

## Data flow (v1)

1. User runs `numbat review` (exact subcommand name TBD at scaffold) with diff target flags
2. Git adapter resolves refs and captures diff + metadata
3. Diff parser builds internal change model
4. Analysis backend adds summary, file groupings, heuristic risk/focus hints
5. Renderer writes to stdout (or file if added later)

## Configuration (planned)

| Mechanism | Purpose |
|---|---|
| CLI flags | Diff target, output format, verbosity |
| Env vars | Optional LLM API key and provider (Phase 3) |
| Config file | Deferred — env + flags sufficient for v1 |

## Open questions

- Exact CLI subcommand tree (`review` vs top-level default)
- JSON schema version field and stability policy
- LLM provider and prompt boundaries (deferred to Phase 3 goal)
- Whether to support diff input from stdin/patch file in v1 (likely deferred)

## Related documents

- `.ai/docs/project-requirements.md`
- `.ai/project/scope.md`
- `.ai/stack-profiles/python-cli.md`
