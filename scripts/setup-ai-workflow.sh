#!/usr/bin/env bash
# Materialize private ai-project-template workflow files into this repository.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="${ROOT}/.ai-template"
AI="${ROOT}/.ai"

if [[ ! -d "${TEMPLATE}/.ai" ]]; then
  git -C "${ROOT}" submodule update --init --recursive .ai-template
fi

if [[ ! -d "${TEMPLATE}/.ai" ]]; then
  echo "error: .ai-template submodule is missing or empty" >&2
  echo "hint: ensure you can read szymoniwacz/ai-project-template" >&2
  exit 1
fi

OVERLAY="$(mktemp -d)"
trap 'rm -rf "${OVERLAY}"' EXIT

cp -a "${AI}/project" "${OVERLAY}/"
if git -C "${ROOT}" ls-files -- .ai/ideas/ 2>/dev/null | grep -q .; then
  mkdir -p "${OVERLAY}"
  (cd "${ROOT}" && git archive HEAD .ai/ideas) | tar -x -C "${OVERLAY}"
fi
cp "${AI}/stack-profiles/diffrat-cli.md" "${OVERLAY}/"
cp "${AI}/architecture/adr-0001-llm-analysis-layer.md" "${OVERLAY}/"
cp "${AI}/docs/architecture-direction.md" "${OVERLAY}/"
cp "${AI}/docs/project-requirements.md" "${OVERLAY}/"

mkdir -p "${AI}"
rsync -a --delete "${TEMPLATE}/.ai/" "${AI}/"

cp -a "${OVERLAY}/project" "${AI}/"
if [[ -d "${OVERLAY}/.ai/ideas" ]]; then
  mkdir -p "${AI}/ideas"
  cp -a "${OVERLAY}/.ai/ideas/." "${AI}/ideas/"
fi
mkdir -p "${AI}/stack-profiles" "${AI}/architecture" "${AI}/docs"
cp "${OVERLAY}/diffrat-cli.md" "${AI}/stack-profiles/"
cp "${OVERLAY}/adr-0001-llm-analysis-layer.md" "${AI}/architecture/"
cp "${OVERLAY}/architecture-direction.md" "${AI}/docs/"
cp "${OVERLAY}/project-requirements.md" "${AI}/docs/"

# Materialize template-owned paths expected by validators and diffrat --check.
rm -rf "${ROOT}/ci" "${ROOT}/examples" \
  "${ROOT}/.github/PULL_REQUEST_TEMPLATE" "${ROOT}/.github/ISSUE_TEMPLATE"
ln -sfn .ai-template/ci "${ROOT}/ci"
ln -sfn .ai-template/examples "${ROOT}/examples"
ln -sfn .ai-template/.cursorrules "${ROOT}/.cursorrules"
ln -sfn ../.ai-template/.github/copilot-instructions.md "${ROOT}/.github/copilot-instructions.md"
ln -sfn ../.ai-template/.github/pull_request_template.md "${ROOT}/.github/pull_request_template.md"
ln -sfn ../.ai-template/.github/PULL_REQUEST_TEMPLATE "${ROOT}/.github/PULL_REQUEST_TEMPLATE"
ln -sfn ../.ai-template/.github/ISSUE_TEMPLATE "${ROOT}/.github/ISSUE_TEMPLATE"

echo "AI workflow ready under .ai/ (template + diffrat overlay)"
