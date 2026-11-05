from pathlib import Path

import pytest


def pytest_collection_modifyitems(items):
    """A pasta é a fonte única da categoria de cada teste."""
    root = Path(__file__).parent
    for item in items:
        category = Path(item.path).relative_to(root).parts[0]
        if category in {"unit", "functional", "integration"}:
            item.add_marker(getattr(pytest.mark, category))
