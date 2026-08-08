# Optional LLM analysis

Diffrat is **offline by default**. Heuristic Focus/Risk hints always run without
API keys. Optional LLM adds a narrative **LLM analysis** section (or JSON
`llm_findings`) when you configure `DIFFRAT_LLM_*` — diff-scoped prompts only.

## Quick start

### OpenAI

```bash
export DIFFRAT_LLM_PROVIDER=openai
export DIFFRAT_LLM_API_KEY=sk-...
diffrat review --base main
```

Default model: `gpt-4o-mini` (OpenAI API).

### Ollama (local)

`ollama` requires a base URL — there is no built-in cloud endpoint.

```bash
export DIFFRAT_LLM_PROVIDER=ollama
export DIFFRAT_LLM_API_KEY=local
export DIFFRAT_LLM_BASE_URL=http://localhost:11434/v1
diffrat review --base main
```

Default model: `llama3` (must be available in your Ollama install).

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `DIFFRAT_LLM_PROVIDER` | When LLM enabled | Provider id (e.g. `openai`, `ollama`) |
| `DIFFRAT_LLM_API_KEY` | When LLM enabled | API key or token |
| `DIFFRAT_LLM_BASE_URL` | For local/custom endpoints | API root ending in `/v1` (not `/chat/completions`) |

Both `DIFFRAT_LLM_PROVIDER` and `DIFFRAT_LLM_API_KEY` must be set to enable LLM.
Partial configuration prints a warning and stays disabled.

Other OpenAI-compatible runtimes (LM Studio, proxies) work via `DIFFRAT_LLM_BASE_URL`.

## Output

### Text report

On success, a **LLM analysis** section appears after Focus/Risk. On failure, the
heuristic report is unchanged; see stderr for an actionable warning.

### JSON (`--json`)

When LLM is **disabled**, no `llm_*` keys are present.

When LLM is **enabled and succeeds**:

```json
{
  "llm_status": "ok",
  "llm_findings": "..."
}
```

When LLM is **enabled and fails**:

```json
{
  "llm_status": "failed",
  "llm_error": "LLM authentication failed (401) — check DIFFRAT_LLM_API_KEY"
}
```

Exit code stays `0` on LLM failure — heuristics remain the primary report.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No LLM section; stderr mentions `ollama` and `BASE_URL` | Ollama without base URL | Set `DIFFRAT_LLM_BASE_URL=http://localhost:11434/v1` |
| `authentication failed (401)` | Invalid or missing API key | Check `DIFFRAT_LLM_API_KEY` |
| `endpoint not found (404)` | Wrong base URL | Use API root (`…/v1`), not `…/chat/completions` |
| `cannot reach LLM endpoint` | Server down or wrong host/port | Start Ollama / proxy; verify URL |
| `timed out` | Slow model or network | Retry; use a faster local model |
| Partial env vars set | Only provider or only key | Set both `DIFFRAT_LLM_PROVIDER` and `DIFFRAT_LLM_API_KEY` |

## Privacy

Diff content leaves your machine only when LLM env vars are set. Never commit
API keys. See ADR-0001 (`.ai/architecture/adr-0001-llm-analysis-layer.md`) and
D-005 in `.ai/project/decisions.md`.
