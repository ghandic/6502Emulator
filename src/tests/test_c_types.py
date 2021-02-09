from hypothesis import given
from hypothesis.strategies import integers
from truth.truth import AssertThat

from ..emulator.c_types import Byte, CType, SByte, Word, s32, u32


def validate_range(val, min, max):
    AssertThat(val).IsAtMost(max)
    AssertThat(val).IsAtLeast(min)
    AssertThat(val + 1).IsAtMost(max)
    AssertThat(val + 1).IsAtLeast(min)
    AssertThat(val - 1).IsAtMost(max)
    AssertThat(val - 1).IsAtLeast(min)
    AssertThat(val << 8).IsAtMost(max)
    AssertThat(val << 8).IsAtLeast(min)
    AssertThat(val >> 8).IsAtMost(max)
    AssertThat(val >> 8).IsAtLeast(min)


def validate_comparison(val, min, max):
    AssertThat(val).IsLessThan(max)
    AssertThat(val).IsGreaterThan(min)


def test_not_implemented():
    with AssertThat(NotImplementedError).IsRaised():
        CType(5)


@given(integers(min_value=-(2 ** 8) - 1, max_value=(2 ** 8) + 1))
def test_byte_range(x):
    validate_range(Byte(x), 0, 2 ** 8)
    validate_comparison(Byte(x), -1, 2 ** 8)


@given(integers(min_value=-(2 ** 16) - 1, max_value=(2 ** 16) + 1))
def test_word_range(x):
    validate_range(Word(x), 0, 2 ** 16)
    validate_comparison(Word(x), -1, 2 ** 16)


@given(integers(min_value=-(2 ** 8) - 1, max_value=(2 ** 8) + 1))
def test_sbyte_range(x):
    validate_range(SByte(x), -(2 ** 8), 2 ** 8)
    validate_comparison(SByte(x), -(2 ** 8), 2 ** 8)


@given(integers(min_value=-(2 ** 32) - 1, max_value=(2 ** 32) + 1))
def test_u32_range(x):
    validate_range(u32(x), 0, 2 ** 32)
    validate_comparison(u32(x), -1, 2 ** 32)


@given(integers(min_value=-(2 ** 32) - 1, max_value=(2 ** 32) + 1))
def test_s32_range(x):
    validate_range(s32(x), -(2 ** 32), 2 ** 32)
    validate_comparison(s32(x), -(2 ** 32), 2 ** 32)
