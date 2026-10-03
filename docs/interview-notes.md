# Interview notes

For each concept NetForge implements: what it is, why NetForge needs it, how it
works, how it fails, how to observe it, alternatives, and likely questions.

## Phase 0: environment

**Why do containers on a Mac need a VM?**
Containers are not virtual machines. They are processes isolated by Linux
kernel features (namespaces, cgroups). macOS has a different kernel (XNU), so
Docker on macOS runs a small Linux VM, and every container, network namespace,
and veth pair lives inside that VM's kernel. Consequence: Linux networking
behaves exactly like Linux, but only inside the VM. The Mac cannot directly
route to container addresses.

**Why a dedicated VM for measurements?**
Timing results depend on CPU scheduling. Sharing a 2-vCPU VM with unrelated
databases adds noise that would be reported as "convergence time". Controlling
and recording the environment is part of a credible measurement.

**What does `make doctor` check, and why from the daemon?**
It asks the Docker daemon (`docker info`) for kernel type, version,
architecture, CPU count, and memory. Those properties belong to the VM, not the
Mac, and they are what the lab actually gets.
