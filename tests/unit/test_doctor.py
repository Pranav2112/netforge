from typing import Any

import pytest

from netforge.doctor import (
    MIN_MEMORY_BYTES,
    CheckResult,
    Status,
    check_docker_context,
    check_docker_info,
    check_python,
    exit_code,
    format_table,
)


def _info(**overrides: Any) -> dict[str, Any]:
    info: dict[str, Any] = {
        "OSType": "linux",
        "KernelVersion": "6.8.0-117-generic",
        "Architecture": "aarch64",
        "NCPU": 4,
        "MemTotal": 6197379072,
    }
    info.update(overrides)
    return info


def _by_name(results: list[CheckResult]) -> dict[str, CheckResult]:
    return {r.name: r for r in results}


@pytest.mark.parametrize(
    ("version", "status"),
    [((3, 12, 14), Status.OK), ((3, 14, 0), Status.OK), ((3, 9, 6), Status.FAIL)],
)
def test_check_python(version: tuple[int, int, int], status: Status) -> None:
    assert check_python(version).status is status


def test_healthy_lab_vm_passes_all_docker_checks() -> None:
    results = check_docker_info(_info())
    assert all(r.status is Status.OK for r in results), results


def test_non_linux_daemon_is_fatal() -> None:
    kernel = _by_name(check_docker_info(_info(OSType="windows")))["docker.kernel"]
    assert kernel.status is Status.FAIL


def test_undersized_vm_warns_but_does_not_fail() -> None:
    # Matches the shared default Colima profile (2 vCPU / 4 GiB).
    results = _by_name(check_docker_info(_info(NCPU=2, MemTotal=4 * 1024**3)))
    assert results["docker.cpus"].status is Status.WARN
    assert results["docker.memory"].status is Status.WARN
    assert exit_code(list(results.values())) == 0


def test_memory_threshold_is_inclusive() -> None:
    mem = _by_name(check_docker_info(_info(MemTotal=MIN_MEMORY_BYTES)))["docker.memory"]
    assert mem.status is Status.OK


def test_missing_fields_degrade_to_warnings() -> None:
    results = _by_name(check_docker_info({"OSType": "linux"}))
    assert results["docker.cpus"].status is Status.WARN
    assert results["docker.memory"].status is Status.WARN


@pytest.mark.parametrize(
    ("active", "expected", "status"),
    [
        ("colima-netforge", "colima-netforge", Status.OK),
        ("colima", "colima-netforge", Status.WARN),
        ("default", None, Status.OK),
    ],
)
def test_check_docker_context(active: str, expected: str | None, status: Status) -> None:
    assert check_docker_context(active, expected).status is status


def test_exit_code_fails_only_on_fail() -> None:
    warn = CheckResult("a", Status.WARN, "")
    fail = CheckResult("b", Status.FAIL, "")
    assert exit_code([warn]) == 0
    assert exit_code([warn, fail]) == 1


def test_format_table_aligns_names() -> None:
    table = format_table([CheckResult("a", Status.OK, "x"), CheckResult("long", Status.FAIL, "y")])
    assert table.splitlines() == ["[OK  ] a     x", "[FAIL] long  y"]
