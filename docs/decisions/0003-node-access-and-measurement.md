# 0003: Node access via `docker exec`; timing measured inside the VM

**Status:** accepted (Phase 0, implemented from Phase 5)

## Context

On macOS the host cannot route to lab addresses inside the VM. Each
`docker exec` round trip also adds tens of milliseconds of variable latency.

## Decision

- The CLI reaches nodes only through `docker exec` (behind an executor
  interface, so logic can be unit tested with a fake).
- Time-sensitive measurements are taken *inside* the lab: high-rate probes
  (`ping -D`), `ip -ts monitor route`, and FRR logs with microsecond
  timestamps. All containers share the VM kernel's clock, so their timestamps
  are directly comparable, with no cross-host clock synchronization needed.

## Consequences

- The same code works on macOS and Linux CI.
- Reported timings exclude tooling overhead, but they reflect a virtualized
  environment. Every result records VM size, kernel, and architecture.
