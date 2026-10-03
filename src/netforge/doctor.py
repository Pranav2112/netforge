"""Preflight checks for the NetForge development environment.

The lab runs inside a Linux VM (Colima on macOS, the host kernel on Linux CI).
Before building topologies or trusting timing measurements we want to know,
from the Docker daemon itself, which kernel and how much CPU/memory the lab
will actually get. The evaluation functions are pure so they can be unit
tested without Docker; only `collect_*` functions touch the system.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

MIN_PYTHON = (3, 12)
MIN_CPUS = 4
# A 6 GiB VM reports ~5.8 GiB to Docker after kernel reservations.
MIN_MEMORY_BYTES = 5 * 1024**3
COMMAND_TIMEOUT_S = 15.0


class Status(StrEnum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Status
    detail: str


def check_python(version: Sequence[int]) -> CheckResult:
    found = ".".join(str(part) for part in version[:3])
    if tuple(version[:2]) >= MIN_PYTHON:
        return CheckResult("python", Status.OK, found)
    wanted = ".".join(map(str, MIN_PYTHON))
    return CheckResult("python", Status.FAIL, f"{found} (need >= {wanted})")


def check_docker_info(info: Mapping[str, Any]) -> list[CheckResult]:
    """Evaluate `docker info` JSON for the properties the lab depends on."""
    results: list[CheckResult] = []

    os_type = info.get("OSType", "unknown")
    kernel = info.get("KernelVersion", "unknown")
    if os_type == "linux":
        results.append(CheckResult("docker.kernel", Status.OK, f"linux {kernel}"))
    else:
        # veth, netns and FRR's zebra all require a Linux kernel.
        results.append(CheckResult("docker.kernel", Status.FAIL, f"{os_type} {kernel}"))

    results.append(CheckResult("docker.arch", Status.OK, str(info.get("Architecture", "unknown"))))

    cpus = int(info.get("NCPU", 0))
    cpu_status = Status.OK if cpus >= MIN_CPUS else Status.WARN
    results.append(CheckResult("docker.cpus", cpu_status, f"{cpus} (want >= {MIN_CPUS})"))

    mem = int(info.get("MemTotal", 0))
    mem_status = Status.OK if mem >= MIN_MEMORY_BYTES else Status.WARN
    results.append(
        CheckResult(
            "docker.memory",
            mem_status,
            f"{mem / 1024**3:.1f} GiB (want >= {MIN_MEMORY_BYTES / 1024**3:.0f} GiB)",
        )
    )
    return results


def check_docker_context(active: str, expected: str | None) -> CheckResult:
    if expected is None or active == expected:
        return CheckResult("docker.context", Status.OK, active)
    # Not fatal: the lab still works, but measurements would share a VM
    # with unrelated workloads.
    return CheckResult("docker.context", Status.WARN, f"{active} (expected {expected})")


def _run(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        args, capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S, check=False
    )


def collect_docker(expected_context: str | None) -> list[CheckResult]:
    docker = shutil.which("docker")
    if docker is None:
        return [CheckResult("docker.cli", Status.FAIL, "docker not found on PATH")]
    results = [CheckResult("docker.cli", Status.OK, docker)]

    try:
        context = _run([docker, "context", "show"])
        info = _run([docker, "info", "--format", "{{json .}}"])
    except subprocess.TimeoutExpired as exc:
        return [*results, CheckResult("docker.daemon", Status.FAIL, f"timed out: {exc.cmd}")]

    if context.returncode == 0:
        results.append(check_docker_context(context.stdout.strip(), expected_context))

    if info.returncode != 0:
        detail = info.stderr.strip().splitlines()[-1] if info.stderr.strip() else "no output"
        return [*results, CheckResult("docker.daemon", Status.FAIL, detail)]
    results.append(CheckResult("docker.daemon", Status.OK, "reachable"))
    return [*results, *check_docker_info(json.loads(info.stdout))]


def run_checks(expected_context: str | None) -> list[CheckResult]:
    return [check_python(sys.version_info[:3]), *collect_docker(expected_context)]


def exit_code(results: Sequence[CheckResult]) -> int:
    return 1 if any(r.status is Status.FAIL for r in results) else 0


def format_table(results: Sequence[CheckResult]) -> str:
    width = max(len(r.name) for r in results)
    return "\n".join(f"[{r.status.upper():4}] {r.name:<{width}}  {r.detail}" for r in results)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the NetForge development environment.")
    parser.add_argument("--expect-context", help="docker context the lab should use")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    results = run_checks(args.expect_context)
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        print(format_table(results))
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
