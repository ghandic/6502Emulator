import warnings

import pytest

from ..emulator.m6502 import CPU

warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture
def cpu():
    return CPU()
