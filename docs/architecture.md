# Architecture

## Layers

```
┌──────────────────────────── host (macOS / Linux) ───────────────────────────┐
│ netforge (Python 3.12)                                                       │
│   doctor       environment preflight                               [Phase 0] │
│   model        intent: routers, ASNs, links, addressing            [Phase 5] │
│   exec         run commands on nodes via `docker exec`             [Phase 5] │
│   collect      FRR JSON (vtysh), kernel JSON (ip -j), probes       [Phase 6] │
│   health       compare observed state against intent               [Phase 6] │
│   faults       link / router / session / withdrawal / netem        [Phase 7] │
│   experiments  baseline → inject → measure → recover → report      [Phase 8] │
│   diagnose     hop-by-hop, evidence-based root cause               [Phase 9] │
│   capture      tcpdump orchestration, pcap retrieval               [Phase 9] │
│   change       validate → snapshot → deploy → verify → rollback   [Phase 10] │
├──────────────────────── Docker API (DOCKER_CONTEXT) ─────────────────────────┤
│ Linux VM (Colima "netforge" profile on macOS; the host kernel on Linux CI)   │
│   containerlab: point-to-point veth links between container netns            │
│   routers: FRRouting      hosts: minimal Linux with network tools            │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Key decisions

Recorded as ADRs in [decisions/](decisions/):

1. [Dedicated Colima VM](decisions/0001-dedicated-colima-vm.md)
2. [containerlab over Docker Compose](decisions/0002-containerlab-over-compose.md)
3. [Node access via `docker exec`, measurements inside the VM](decisions/0003-node-access-and-measurement.md)

## Repository layout

| Path | Purpose |
|---|---|
| `src/netforge/` | Python package (src layout so tests import the installed package) |
| `lab/` | Topology, node configs, container images |
| `tests/unit` | Pure logic, no Docker |
| `tests/integration` | Needs a Docker daemon (marker `integration`) |
| `tests/scenarios` | Needs a running lab (marker `scenario`) |
| `experiments/results/` | Committed, machine-generated measurement results |
| `captures/` | Local packet captures (gitignored) |
| `scripts/` | Shell helpers (shellchecked in CI) |
