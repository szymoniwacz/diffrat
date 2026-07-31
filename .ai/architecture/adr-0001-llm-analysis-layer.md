# ADR-0001 — Phase 3 optional LLM analysis layer

## Status

`Accepted`

Owner material decisions on Project Execution issue #71 (2026-07-31):
`1: A`, `2: Y, Y, Y`, `3: B`.

## Context

Numbat v1 closed on the Phase 2 static core (deterministic Focus/Risk hints and
file categories). D-005 originally skipped Phase 3 LLM work for v1. Project
Execution #71 reopens optional LLM analysis with explicit owner choices for
provider architecture, data handling, and secrets contract.

The product must remain useful offline without API keys. When configured, LLM
findings augment — never replace — the heuristic report. Prompts must be
diff-scoped; no whole-repo scan or implicit network use.

## Decision

### Provider architecture

Use a **single OpenAI-compatible HTTP client** as the only LLM integration path
for Phase 3 v1. The client targets cloud providers (OpenAI and other
OpenAI-shaped APIs) and local runtimes (Ollama, LM Studio, etc.) through an
optional custom base URL. No first-class multi-provider adapter layer in the
initial Phase 3 slice.

### Data handling

| Policy | Requirement |
|---|---|
| Opt-in only | No network calls unless LLM env/config is explicitly set |
| Diff-scoped prompts | Send only bounded diff content from the current review; never whole-repo or file-tree scan |
| Heuristics default | Deterministic heuristic report always runs; LLM findings are additive |

### Environment variable contract

| Variable | Required | Purpose |
|---|---|---|
| `NUMBAT_LLM_PROVIDER` | When LLM enabled | Provider identifier (e.g. `openai`, `ollama`) |
| `NUMBAT_LLM_API_KEY` | When LLM enabled | API key or token for the configured provider |
| `NUMBAT_LLM_BASE_URL` | Optional | Custom endpoint for local runtimes or OpenAI-compatible proxies |

Cloud provider default endpoints are hardcoded per `NUMBAT_LLM_PROVIDER` value.
`NUMBAT_LLM_BASE_URL` is for local/custom endpoints only.

### Analysis backend boundary

The analysis backend selects heuristics-only or heuristics-plus-LLM based on
configuration. The diff parser and git adapter remain network-free. The LLM
client lives behind the analysis backend and is invoked only when opt-in config
is present.

## Alternatives considered

| Alternative | Why not chosen |
|---|---|
| First-class multi-provider adapters (OpenAI + Anthropic, extensible) | Larger surface and maintenance; owner chose smallest single code path (1:A) |
| Anthropic-only for Phase 3 v1 | Excludes local runtimes and OpenAI-shaped APIs without extra adapters |
| Local runtime only (no cloud) | Owner wants cloud + local via one OpenAI-compatible client |
| Provider-specific keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) without shared prefix | Owner chose unified `NUMBAT_LLM_*` prefix with optional base URL (3:B) |
| `NUMBAT_LLM_*` without base URL env | Cannot reach local/custom endpoints without code changes per runtime |

## Consequences

### Positive

- One HTTP client and request shape to implement and test
- Local and cloud providers share configuration pattern
- Clear opt-in boundary preserves offline-first default
- Additive LLM findings avoid breaking deterministic report consumers

### Negative

- Non-OpenAI-shaped APIs need a compatibility layer or future adapter work
- Provider-specific features (tool use, native Anthropic messages) are out of scope
- Base URL misconfiguration can send diff content to unintended endpoints

### Follow-up

- [ ] Pluggable analysis backend: heuristics default; LLM when configured
- [ ] Document env vars and privacy in README
- [ ] Surface LLM findings in text report and `--json` (additive fields)
- [ ] Tests with mocked LLM HTTP client; no live integration required in CI

## Validation

- [x] Implementation matches decision — docs record owner-approved choices
- [x] Docs updated — D-005, architecture direction, FR-008 reference ADR
- [ ] Risks reviewed — pending implementation PR review

## Date

2026-07-31
