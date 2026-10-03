import shutil

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip Docker-dependent tests when no docker CLI is installed.

    If the CLI exists but the daemon is down, the test runs and fails loudly:
    that is a broken environment, not a reason to skip.
    """
    if shutil.which("docker") is not None:
        return
    skip = pytest.mark.skip(reason="docker CLI not installed")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
