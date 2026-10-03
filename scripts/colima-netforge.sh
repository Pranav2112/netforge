#!/usr/bin/env bash
# Manage the dedicated Colima VM that hosts the NetForge lab (macOS only).
#
# Colima rewrites the *global* Docker context: `start` switches it to the new
# profile and `stop` can reset it to "default". Either would silently redirect
# every other project's `docker` commands, so we restore whatever the user had.
# NetForge itself selects its VM per-command via DOCKER_CONTEXT (see Makefile).
set -euo pipefail

PROFILE="netforge"
CPUS="${NETFORGE_VM_CPUS:-4}"
MEMORY_GIB="${NETFORGE_VM_MEMORY:-6}"
DISK_GIB="${NETFORGE_VM_DISK:-40}"

die() { echo "error: $*" >&2; exit 1; }

# The Makefile exports DOCKER_CONTEXT, which overrides the global setting we
# need to read and restore here.
global_docker() { env -u DOCKER_CONTEXT docker "$@"; }

# Run a colima command, then put the global docker context back if it moved.
preserving_context() {
  local before after
  before="$(global_docker context show)"
  "$@"
  after="$(global_docker context show)"
  if [[ "$after" != "$before" ]]; then
    global_docker context use "$before" >/dev/null
    echo "restored global docker context: $before (colima had set $after)"
  fi
}

command -v colima >/dev/null || die "colima not installed (brew install colima docker)"
command -v docker >/dev/null || die "docker CLI not installed (brew install docker)"

case "${1:-}" in
  up)
    # Flags apply on first creation; an existing VM keeps its settings
    # (resize with: colima stop -p netforge && colima start -p netforge --cpu N).
    preserving_context colima start --profile "$PROFILE" \
      --cpu "$CPUS" --memory "$MEMORY_GIB" --disk "$DISK_GIB" \
      --arch aarch64 --vm-type vz --mount-type virtiofs --runtime docker
    ;;
  down)
    preserving_context colima stop --profile "$PROFILE"
    ;;
  status)
    colima status --profile "$PROFILE"
    ;;
  *)
    echo "usage: $0 {up|down|status}" >&2
    exit 2
    ;;
esac
