# Troubleshooting log

Real problems hit while building NetForge: symptom, investigation, root cause,
fix, and the guard that prevents a regression.

## T-001: Colima silently rewrites the global Docker context (Phase 0)

**Symptom.** After creating the `netforge` Colima profile, `docker context
show` reported `colima-netforge`. Every other project's `docker` and
`docker compose` commands would now silently target the lab VM instead of the
VM their containers live in.

**Investigation.**
1. `colima start` output included `Current context is now "colima-netforge"`:
   it switches the global context to the new profile.
2. The first fix saved the context before `colima start` and restored it
   afterwards, but a cold-start test showed the restore never ran. The Makefile
   exports `DOCKER_CONTEXT=colima-netforge`, and that variable overrides the
   global setting, so `docker context show` inside the script reported the
   override rather than the user's choice.
3. A further test showed `colima stop`, run with that variable set, resets the
   global context to `default`.

**Root cause.** Colima mutates global Docker state on both start and stop, and
`DOCKER_CONTEXT` masks the global value from any child process.

**Fix.** `scripts/colima-netforge.sh` reads and writes the global context with
`DOCKER_CONTEXT` removed from the environment, and wraps both `start` and `stop`
so the original context is restored if Colima changes it.

**Verified.** Two full `vm-down`/`vm-up` cycles starting from context `colima`
left it as `colima`. A container from another project kept running throughout.
