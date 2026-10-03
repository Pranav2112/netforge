# 0002: containerlab over Docker Compose for topology wiring

**Status:** accepted (Phase 0, implemented in Phase 1)

## Context

Routers need point-to-point links whose failure looks like a real link failure
(loss of carrier) to the routing stack.

## Options

- **Docker Compose networks:** each link is a Docker-managed L2 bridge. Docker
  assigns IPs, injects a gateway address and default route, and installs
  iptables rules between bridges. A link "failure" is `docker network
  disconnect`, which removes the interface rather than dropping carrier.
- **Custom Python netns/veth builder:** full control, but it re-implements a
  mature tool.
- **containerlab:** the de facto standard for container network labs. It creates
  veth pairs directly between container namespaces from a YAML topology and runs
  on GitHub's Linux runners.

## Decision

Use containerlab. Run it from its official container image against the VM's
Docker daemon. If that fails on Colima, install it inside the VM. Phase 1 first
builds a small topology by hand with `ip netns` and veth pairs, so the
mechanism containerlab automates is understood.

## Consequences

- Link failure can be injected as `ip link set <if> down`, which produces a
  real carrier-loss event on the peer.
- containerlab adds a management interface (`eth0`) per node. The routed
  network must never depend on it (see networking.md).
