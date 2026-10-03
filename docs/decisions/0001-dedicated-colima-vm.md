# 0001: Dedicated Colima VM for the lab

**Status:** accepted (Phase 0)

## Context

On macOS, containers run inside a Linux VM. The developer's default Colima VM
(2 vCPU / 4 GiB) already hosts other projects. Convergence and latency
measurements are sensitive to CPU contention, and a shared VM makes results
depend on unrelated workloads.

## Decision

Run the lab in a separate Colima profile, `netforge` (4 vCPU, 6 GiB, 40 GiB
disk, `vz` virtualization, virtiofs mounts). NetForge selects it per command
with `DOCKER_CONTEXT=colima-netforge` and never changes the user's global
Docker context.

## Consequences

- Experiments run on a known, recorded VM size (`make doctor`).
- About 6 GiB of RAM is reserved while the VM runs; `make vm-down` frees it.
- Colima rewrites the global Docker context on start and stop.
  `scripts/colima-netforge.sh` restores it (see troubleshooting T-001).
- The VM kernel lacks `vrf` and `mpls` modules (`linux-modules-extra` is not
  installed). Nothing planned needs them.
