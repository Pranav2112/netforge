# NetForge — Network Automation & Resilience Platform

NetForge is a reproducible, containerized network lab for practicing production
network engineering: building multi-AS BGP topologies with FRRouting, automating
operations in Python, injecting failures, and **measuring** how the network
detects, reroutes, and recovers.

> **Status:** Phase 0 (repository foundation). No network exists yet. This
> README only describes what is built and verified; planned work is marked as such.

## Why

Most networking labs stop once routes appear. Production engineering starts
there: *what happens when a link dies, how long until traffic flows again, and
can a tool tell you why H1 can't reach H4?* NetForge answers those questions
with measurements taken from the running network, not assumptions.

## Planned topology (v1)

Four routers, one private ASN each (the eBGP-only design of
[RFC 7938](https://www.rfc-editor.org/rfc/rfc7938)), connected as a square plus
one diagonal so that every single link or router failure leaves an alternate path.

```
   H1                         H2
   │                          │
   R1 AS65001 ──────────── R2 AS65002
   │                     ╱    │
   │                 ╱        │
   │             ╱            │
   R3 AS65003 ──────────── R4 AS65004
   │                          │
   H3                         H4
```

Addressing and design rationale: [docs/networking.md](docs/networking.md).

## Architecture

A Python CLI on the host drives containers inside a Linux VM through the Docker
API. containerlab wires routers (FRRouting) and hosts with point-to-point veth
links. Details: [docs/architecture.md](docs/architecture.md).

## Quick start

Requirements: macOS on Apple Silicon or Linux, [uv](https://docs.astral.sh/uv/),
Docker CLI, and on macOS [Colima](https://github.com/abiosoft/colima).

```bash
make vm-up     # macOS: dedicated 4 vCPU / 6 GiB Colima VM (global docker context is preserved)
make sync      # locked Python 3.12 environment
make doctor    # verify Python, Docker daemon, Linux kernel, VM sizing
make check     # format, lint, type-check, unit tests (what CI runs)
```

On Linux, skip `vm-up` and pass `NETFORGE_DOCKER_CONTEXT=default`.

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 0 | Repository foundation, tooling, CI, lab VM | done |
| 1 | Container topology (manual netns, then containerlab) | planned |
| 2 | IP addressing, static routing, troubleshooting | planned |
| 3 | FRRouting integration | planned |
| 4 | eBGP topology and route propagation | planned |
| 5 | Python CLI and intent model | planned |
| 6 | Monitoring and state collection | planned |
| 7 | Failure injection | planned |
| 8 | Convergence measurement, BFD | planned |
| 9 | Diagnosis and packet analysis | planned |
| 10 | Configuration validation and rollback | planned |
| 11 | Transit AS with IS-IS + iBGP (if justified) | planned |
| 12 | Benchmarks and final documentation | planned |

## Documentation

- [Architecture](docs/architecture.md)
- [Networking design](docs/networking.md)
- [Experiments](docs/experiments.md): methodology and measured results
- [Troubleshooting](docs/troubleshooting.md): real problems hit and how they were diagnosed
- [Interview notes](docs/interview-notes.md)
- [Decision records](docs/decisions/)

## License

[MIT](LICENSE)
