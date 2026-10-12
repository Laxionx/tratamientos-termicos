import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tratamientos.equilibrio import DEFAULT_DATABASE  # noqa: E402


@pytest.fixture(scope="session")
def database():
    if not DEFAULT_DATABASE.is_file():
        pytest.skip(f"falta la base {DEFAULT_DATABASE.name}; ver README")
    return DEFAULT_DATABASE
