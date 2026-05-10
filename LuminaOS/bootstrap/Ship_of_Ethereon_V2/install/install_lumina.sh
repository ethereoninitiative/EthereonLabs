#!/usr/bin/env bash
set -euo pipefail

# Lumina local installer.
# Creates a user-local symlink named `lumina` pointing to the bootstrap host entrypoint.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LUMINA_BIN="${BOOTSTRAP_ROOT}/bin/lumina"
INSTALL_DIR="${HOME}/.local/bin"
TARGET="${INSTALL_DIR}/lumina"

mkdir -p "${INSTALL_DIR}"
chmod +x "${LUMINA_BIN}" || true
ln -sfn "${LUMINA_BIN}" "${TARGET}"

echo "Lumina host command installed: ${TARGET}"
echo ""
echo "Try:"
echo "  lumina doctor"
echo "  lumina run \"Review Lumina OS progress and produce the next governed action receipt.\""
echo "  lumina observe"
echo "  lumina state"
echo "  lumina studio"
echo ""
case ":${PATH}:" in
  *":${INSTALL_DIR}:"*) ;;
  *)
    echo "Note: ${INSTALL_DIR} is not currently on PATH."
    echo "Add this to your shell profile if needed:"
    echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
    ;;
esac
