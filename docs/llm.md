# Optional LLM analysis

Diffrat is offline-first. Heuristic Focus/Risk analysis always runs with no
network calls. LLM analysis is **opt-in only** via `DIFFRAT_LLM_*` environment
variables.

When enabled and the request succeeds, the text report gains an **LLM analysis**
section and `--json` output includes additive `llm_status` / `llm_findings`
fields. When enabled and the request fails, stderr shows an actionable warning
and JSON includes `llm_status: "failed"` and `llm_error`. Exit code stays `0`;
the heuristic report is unchanged on LLM failure.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `DIFFRAT_LLM_PROVIDER` | When LLM enabled | Provider id (e.g. `openai`, `ollama`) |
| `DIFFRAT_LLM_API_KEY` | When LLM enabled | API key or token |
| `DIFFRAT_LLM_BASE_URL` | For local/custom providers | OpenAI-compatible API **root** URL |

`DIFFRAT_LLM_BASE_URL` must be the API root (for example
`http://localhost:11434/v1`), **not** the full `/chat/completions` path.

Default models when no model env var is set:

| Provider | Default model |
|---|---|
| `openai` | `gpt-4o-mini` |
| `ollama` | `llama3` |

## OpenAI (cloud)

```bash
export DIFFRAT_LLM_PROVIDER=openai
export DIFFRAT_LLM_API_KEY=sk-your-key-here
diffrat review --json
```

## Ollama (local)

Start Ollama, pull a model (for example `ollama pull llama3`), then:

```bash
export DIFFRAT_LLM_PROVIDER=ollama
export DIFFRAT_LLM_API_KEY=ollama          # any non-empty token
export DIFFRAT_LLM_BASE_URL=http://localhost:11434/v1
diffrat review --json
```

## JSON LLM fields

When LLM is **disabled** (no env vars), JSON omits all `llm_*` keys.

When LLM is **enabled and succeeds**:

```json
{
  "llm_status": "ok",
  "llm_findings": "Review focus: ..."
}
```

When LLM is **enabled and fails**:

```json
{
  "llm_status": "failed",
  "llm_error": "LLM authentication failed (HTTP 401): ..."
}
```

`schema_version` remains `"1"`; these fields are additive.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `provider 'ollama' requires DIFFRAT_LLM_BASE_URL` | Set `DIFFRAT_LLM_BASE_URL` to your API root (e.g. `http://localhost:11434/v1`) |
| `DIFFRAT_LLM_BASE_URL must be the API root ... not ... /chat/completions` | Remove `/chat/completions` from the base URL |
| `LLM authentication failed (HTTP 401)` | Check `DIFFRAT_LLM_API_KEY` |
| `LLM endpoint not found (HTTP 404)` | Verify `DIFFRAT_LLM_BASE_URL` and that the server exposes `/v1/chat/completions` |
| `LLM connection refused` | Start the local server or fix the host/port in `DIFFRAT_LLM_BASE_URL` |
| `incomplete LLM configuration` | Set **both** `DIFFRAT_LLM_PROVIDER` and `DIFFRAT_LLM_API_KEY` |

**Privacy:** diff content leaves the machine only when LLM env vars are set.
Never commit API keys. See ADR-0001 and D-005 in `.ai/project/decisions.md`.
