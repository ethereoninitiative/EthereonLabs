#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/ethereoninitiative/EthereonLabs.git}"
REPO_ROOT="${REPO_ROOT:-/opt/lumina/EthereonLabs}"
SERVICE_USER="${SERVICE_USER:-lumina}"
STATE_ROOT="${STATE_ROOT:-/var/lib/lumina}"
LOG_ROOT="${LOG_ROOT:-/var/log/lumina}"
ENV_DIR="/etc/lumina"
ENV_FILE="${ENV_DIR}/lumina-appliance.env"

require_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run as root or through sudo."
    exit 1
  fi
}

install_packages() {
  apt-get update
  apt-get install -y \
    git \
    curl \
    python3 \
    python3-venv \
    python3-pip \
    nodejs \
    npm \
    postgresql \
    postgresql-contrib
}

ensure_service_user() {
  if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
    useradd --system --create-home --shell /bin/bash "${SERVICE_USER}"
  fi
}

prepare_directories() {
  install -d -o "${SERVICE_USER}" -g "${SERVICE_USER}" "${STATE_ROOT}"
  install -d -o "${SERVICE_USER}" -g "${SERVICE_USER}" "${LOG_ROOT}"
  install -d -o root -g root "${ENV_DIR}"
  install -d -o "${SERVICE_USER}" -g "${SERVICE_USER}" "$(dirname "${REPO_ROOT}")"
}

checkout_repo() {
  if [[ ! -d "${REPO_ROOT}/.git" ]]; then
    sudo -u "${SERVICE_USER}" git clone "${REPO_URL}" "${REPO_ROOT}"
  else
    sudo -u "${SERVICE_USER}" git -C "${REPO_ROOT}" pull --ff-only
  fi
}

install_node_dependencies() {
  sudo -u "${SERVICE_USER}" npm --prefix "${REPO_ROOT}/chamber-app" install
  sudo -u "${SERVICE_USER}" npm --prefix "${REPO_ROOT}/chamber-app" run build
}

write_env_template() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    cat > "${ENV_FILE}" <<'EOF'
PYTHONUNBUFFERED=1
CHAMBER_PUBLIC_ROOM_SLUG=public-room-one
SESSION_TTL_HOURS=168
CHAMBER_ALLOWED_ORIGINS=http://localhost:3000,https://example.com
CHAMBER_STORE_MODE=postgres
CHAMBER_ADVISORY_PORT=8788
DATABASE_URL=postgres://SET_USER:SET_PASSWORD@localhost:5432/SET_DBNAME
EOF
    chmod 600 "${ENV_FILE}"
  fi
}

initialize_database() {
  sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='chamber'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE ROLE chamber LOGIN PASSWORD 'change-me';"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='chamber'" | grep -q 1 || \
    sudo -u postgres createdb -O chamber chamber
  sudo -u postgres psql -d chamber -f "${REPO_ROOT}/chamber_data_model_r1.sql"
  sudo -u postgres psql -d chamber -f "${REPO_ROOT}/chamber_sessions_extension_r1.sql"
  sudo -u postgres psql -d chamber -f "${REPO_ROOT}/chamber_advisory_queue_extension_r1.sql"
}

install_systemd_units() {
  cp "${REPO_ROOT}/deploy/ubuntu_server_lts/lumina-orchestrator.service" /etc/systemd/system/
  cp "${REPO_ROOT}/deploy/ubuntu_server_lts/lumina-orchestrator.timer" /etc/systemd/system/
  cp "${REPO_ROOT}/deploy/ubuntu_server_lts/chamber-advisory.service" /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable chamber-advisory.service
  systemctl enable lumina-orchestrator.timer
}

start_services() {
  systemctl restart chamber-advisory.service
  systemctl restart lumina-orchestrator.timer
}

main() {
  require_root
  install_packages
  ensure_service_user
  prepare_directories
  checkout_repo
  install_node_dependencies
  write_env_template
  initialize_database
  install_systemd_units
  start_services
  echo "Lumina Appliance bootstrap scaffold complete. Review ${ENV_FILE} and change placeholder database credentials."
}

main "$@"
