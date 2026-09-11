#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
GUI_DIR="${REPO_ROOT}/GUI"
PYTHON="${REPO_ROOT}/.venv/bin/python"
CONFIG="config_real_can.xml"
HOST="127.0.0.1"
PORT="8765"
REST_URL="http://${HOST}:${PORT}/api/v1"
BACKEND_PID=""

cleanup() {
    if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
        kill "${BACKEND_PID}" 2>/dev/null || true
        wait "${BACKEND_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

if [[ ! -x "${PYTHON}" ]]; then
    echo "Project virtual environment not found: ${PYTHON}" >&2
    exit 1
fi

if ! command -v ip >/dev/null 2>&1; then
    echo "The ip command is required to verify the CAN interface." >&2
    exit 1
fi

if ! ip link show can0 >/dev/null 2>&1; then
    echo "CAN interface can0 was not found. Configure the CAN device first." >&2
    exit 1
fi

if ! ip link show can0 | grep -q "state UP"; then
    echo "CAN interface can0 is not UP." >&2
    exit 1
fi

cd "${GUI_DIR}"
"${PYTHON}" main.py \
    --config "${CONFIG}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --channel can0 \
    > "${REPO_ROOT}/integration_backend.log" 2>&1 &
BACKEND_PID=$!

for _ in $(seq 1 50); do
    if ! kill -0 "${BACKEND_PID}" 2>/dev/null; then
        echo "Backend exited before opening port ${PORT}." >&2
        cat "${REPO_ROOT}/integration_backend.log" >&2 || true
        exit 1
    fi
    if (echo >/dev/tcp/${HOST}/${PORT}) >/dev/null 2>&1; then
        break
    fi
    sleep 0.1
done

if ! (echo >/dev/tcp/${HOST}/${PORT}) >/dev/null 2>&1; then
    echo "Backend did not open port ${PORT}." >&2
    cat "${REPO_ROOT}/integration_backend.log" >&2 || true
    exit 1
fi

export PROCESS_CONTROL_REST_URL="${REST_URL}"
"${PYTHON}" -m pytest tests -m integration_tests -q
