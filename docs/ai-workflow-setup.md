# Private AI workflow setup

Numbat keeps product code public. The reusable AI workflow lives in the
private submodule `.ai-template/` (`szymoniwacz/ai-project-template`).

**CLI users and external testers do not need this document.** To install and
run `numbat review`, follow the product Setup section in `README.md`
(`git clone` + `pip install -e .`). This page is only for maintainers and
contributors who need the AI working system or full local CI contract
validation.

## Local setup

```bash
git clone --recurse-submodules git@github.com:szymoniwacz/numbat.git
cd numbat
./scripts/setup-ai-workflow.sh
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive .ai-template
./scripts/setup-ai-workflow.sh
```

After setup, `.ai/` is a local merge of the private template plus committed
numbat product files under `.ai/project/`, `.ai/docs/project-requirements.md`,
and related paths.

## Full workflow validation (local)

```bash
./scripts/validate-ai-workflow.sh
```

## GitHub Actions

CI reads the private submodule via deploy key secret `SUBMODULE_DEPLOY_KEY`
(read-only key on `ai-project-template`). Repository maintainers configure this
once in numbat Settings → Secrets and variables → Actions.

## What stays public in numbat

- `src/numbat/`, `tests/`, product `README.md`
- Numbat product context: `.ai/project/`, `numbat-cli.md`, product ADR/docs
- Thin adapters: `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`

## What is private

Everything else under `.ai/` and template-owned paths (`ci/`, `examples/`,
selected `.github/` adapters) are symlinked from `.ai-template/` by the setup
script and are not committed to the public repository.
