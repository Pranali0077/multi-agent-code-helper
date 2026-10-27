import os
import pytest

def pytest_collection_modifyitems(config, items):
    """Skip tests marked as live unless RUN_LIVE=1 is set."""
    if os.environ.get("RUN_LIVE") == "1":
        return
    skip_live = pytest.mark.skip(reason="requires RUN_LIVE=1 and network/keys")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
