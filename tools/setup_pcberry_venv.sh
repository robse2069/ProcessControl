#!/usr/bin/env bash
set -euo pipefail

# Install host prerequisites required by the GUI, CAN diagnostics, and Python venv.
if [[ "$(id -u)" -eq 0 ]]; then
    apt-get update
    apt-get install -y python3 python3-venv python3-tk can-utils
elif command -v sudo >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-tk can-utils
else
    echo "sudo is required to install Raspbian packages: python3-venv, python3-tk, and can-utils" >&2
    exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"
PYTHON="${VENV_DIR}/bin/python"

if [[ ! -x "${PYTHON}" ]]; then
    python3 -m venv "${VENV_DIR}"
fi

"${PYTHON}" -m pip install --upgrade pip
"${PYTHON}" -m pip install --upgrade python-can

"${PYTHON}" - <<'PY'
import can
import tkinter

print(f"python-can: {can.__version__}")
print("tkinter: available")
PY

cat <<EOF

Setup complete.
Virtual environment: ${VENV_DIR}
Activate it with:
  source ${VENV_DIR}/bin/activate
EOF
