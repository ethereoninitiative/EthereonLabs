#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/opt/lumina/EthereonLabs}"
ENV_FILE="${ENV_FILE:-/etc/lumina/lumina-appliance.env}"
LOG_ROOT="${LOG_ROOT:-/var/log/lumina}"
STATE_ROOT="${STATE_ROOT:-/var/lib/lumina}"

pass() {
  echo "[PASS] $1"
}

fail() {
  echo "[FAIL] $1"
  exit 1
}

check_command() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    pass "command available: $cmd"
  else
    fail "missing command: $cmd"
  fi
}

check_file() {
  local path="$1"
  [[ -f "$path" ]] && pass "file exists: $path" || fail "missing file: $path"
}

check_dir() {
  local path="$1"
  [[ -d "$path" ]] && pass "directory exists: $path" || fail "missing directory: $path"
}

check_systemd_unit() {
  local unit="$1"
  if systemctl list-unit-files "$unit" >/dev/null 2>&1; then
    pass "systemd unit visible: $unit"
  else
    fail "systemd unit not found: $unit"
  fi
}

main() {
  check_command python3
  check_command node
  check_command npm
  check_command psql
  check_command systemctl

  check_dir "$REPO_ROOT"
  check_dir "$REPO_ROOT/deploy/ubuntu_server_lts"
  check_dir "$REPO_ROOT/chamber-app"
  check_file "$REPO_ROOT/chamber_data_model_r1.sql"
  check_file "$REPO_ROOT/chamber_sessions_extension_r1.sql"
  check_file "$REPO_ROOT/chamber_advisory_queue_extension_r1.sql"
  check_file "$ENV_FILE"

  check_dir "$LOG_ROOT"
  check_dir "$STATE_ROOT"

  check_systemd_unit lumina-orchestrator.service
  check_systemd_unit lumina-orchestrator.timer
  check_systemd_unit chamber-advisory.service

  pass "Lumina appliance preflight completed"
}

main "$@"
