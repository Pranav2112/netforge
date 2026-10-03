"""Run the doctor against the real Docker daemon (local VM or CI runner)."""

import pytest

from netforge.doctor import Status, run_checks

pytestmark = pytest.mark.integration


def test_docker_daemon_is_linux_and_reachable() -> None:
    results = {r.name: r for r in run_checks(expected_context=None)}
    assert results["docker.daemon"].status is Status.OK, results["docker.daemon"]
    assert results["docker.kernel"].status is Status.OK, results["docker.kernel"]
