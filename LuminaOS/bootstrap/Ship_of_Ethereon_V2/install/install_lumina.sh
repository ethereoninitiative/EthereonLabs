#!/usr/bin/env bash
set -euo pipefail

# Lumina local installer.
# Creates a user-local symlink named `lumina` pointing to the bootstrap host entrypoint.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LUMINA_BIN="${BOOTSTRAP_ROOT}/bin/lumina"
DOCTOR="${BOOTSTRAP_ROOT}/install/lumina_doctor.py"
INSTALL_DIR="${LUMINA_INSTALL_DIR:-${HOME}/.local/bin}"
TARGET="${INSTALL_DIR}/lumina"

usage() {
  cat <<'EOF'
Usage: bash install/install_lumina.sh [--uninstall] [--doctor] [--ensure-state] [--migrate-state]

Options:
  --uninstall      Remove the user-local lumina symlink if it points to this checkout.
  --doctor         Run the Lumina doctor after install.
  --ensure-state   Create the local .lumina_state schema marker through the doctor.
  --migrate-state  Migrate a known older local state schema marker through the doctor.

Environment:
  LUMINA_INSTALL_DIR  Override install directory. Defaults to $HOME/.local/bin.
EOF
}

UNINSTALL=0
RUN_DOCTOR=0
ENSURE_STATE=0
MIGRATE_STATE=0

for arg in "$@"; do
  case "${arg}" in
    --uninstall) UNINSTALL=1 ;;
    --doctor) RUN_DOCTOR=1 ;;
    --ensure-state) ENSURE_STATE=1 ;;
    --migrate-state) MIGRATE_STATE=1 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: ${arg}" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -f "${LUMINA_BIN}" ]]; then
  echo "Lumina host entrypoint missing: ${LUMINA_BIN}" >&2
  exit 1
fi

if [[ ! -f "${DOCTOR}" ]]; then
  echo "Lumina doctor missing: ${DOCTOR}" >&2
  exit 1
fi

if [[ ${UNINSTALL} -eq 1 ]]; then
  if [[ -L "${TARGET}" ]]; then
    CURRENT_TARGET="$(readlink "${TARGET}")"
    if [[ "${CURRENT_TARGET}" == "${LUMINA_BIN}" ]]; then
      rm "${TARGET}"
      echo "Removed Lumina host command: ${TARGET}"
    else
      echo "Refusing to remove ${TARGET}; it points to ${CURRENT_TARGET}, not this checkout."
      exit 1
    fi
  elif [[ -e "${TARGET}" ]]; then
    echo "Refusing to remove ${TARGET}; it exists but is not a symlink."
    exit 1
  else
    echo "Lumina host command is not installed at ${TARGET}"
  fi
  exit 0
fi

mkdir -p "${INSTALL_DIR}"
chmod +x "${LUMINA_BIN}" "${DOCTOR}" || true

if [[ -e "${TARGET}" && ! -L "${TARGET}" ]]; then
  echo "Refusing to overwrite non-symlink target: ${TARGET}" >&2
  exit 1
fi

if [[ -L "${TARGET}" ]]; then
  CURRENT_TARGET="$(readlink "${TARGET}")"
  if [[ "${CURRENT_TARGET}" != "${LUMINA_BIN}" ]]; then
    echo "Replacing existing Lumina symlink: ${TARGET} -> ${CURRENT_TARGET}"
  fi
fi

ln -sfn "${LUMINA_BIN}" "${TARGET}"

DOCTOR_ARGS=()
if [[ ${ENSURE_STATE} -eq 1 ]]; then
  DOCTOR_ARGS+=("--ensure-state")
fi
if [[ ${MIGRATE_STATE} -eq 1 ]]; then
  DOCTOR_ARGS+=("--migrate-state")
fi

if [[ ${RUN_DOCTOR} -eq 1 || ${ENSURE_STATE} -eq 1 || ${MIGRATE_STATE} -eq 1 ]]; then
  echo "Running Lumina doctor..."
  python3 "${DOCTOR}" "${DOCTOR_ARGS[@]}"
fi

echo "Lumina host command installed: ${TARGET}"
echo "Bootstrap root: ${BOOTSTRAP_ROOT}"
echo ""
echo "Try:"
echo "  lumina doctor"
echo "  lumina run \"Review Lumina OS progress and produce the next governed action receipt.\""
echo "  lumina observe"
echo "  lumina state"
echo "  lumina studio"
echo ""
echo "State setup/migration:"
echo "  bash install/install_lumina.sh --ensure-state"
echo "  bash install/install_lumina.sh --migrate-state"
echo ""
echo "Reset/remove:"
echo "  bash install/install_lumina.sh --uninstall"
echo ""
case ":${PATH}:" in
  *":${INSTALL_DIR}:"*) ;;
  *)
    echo "Note: ${INSTALL_DIR} is not currently on PATH."
    echo "Add this to your shell profile if needed:"
    echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
    ;;
esac
