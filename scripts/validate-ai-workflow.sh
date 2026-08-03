#!/usr/bin/env bash
# Validate numbat against the private workflow template contracts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"${ROOT}/scripts/setup-ai-workflow.sh"

python "${ROOT}/.ai-template/ci/validate-workflow-contracts.py" --mode project --root "${ROOT}"
python "${ROOT}/.ai-template/ci/tests/test_validator.py"
python "${ROOT}/.ai-template/ci/tests/test_project_validator.py"
python "${ROOT}/.ai-template/ci/tests/test_folder_map_validation.py"
python "${ROOT}/.ai-template/ci/tests/test_ci_validation_mode.py"
