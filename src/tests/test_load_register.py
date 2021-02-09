import copy

import pytest
from truth.truth import AssertThat

from ..emulator.const import OpCodes


def verify_unmodified_flags_from_loading_register(cpu, cpu_copy):
    AssertThat(cpu.Flag.C).IsEqualTo(cpu_copy.Flag.C)
    AssertThat(cpu.Flag.I).IsEqualTo(cpu_copy.Flag.I)
    AssertThat(cpu.Flag.D).IsEqualTo(cpu_copy.Flag.D)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.V).IsEqualTo(cpu_copy.Flag.V)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_IM, "A"), (OpCodes.INS_LDX_IM, "X"), (OpCodes.INS_LDY_IM, "Y")],
    ids=[
        "LDA Immediate Can Load A Value Into The A Register",
        "LDX Immediate Can Load A Value Into The X Register",
        "LDY Immediate Can Load A Value Into The Y Register",
    ],
)
def test_load_register_immediate(cpu, op_code, register):
    # Given
    expected_cycles = 2
    stored_value = 0x84
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsTruthy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_ZP, "A"), (OpCodes.INS_LDX_ZP, "X"), (OpCodes.INS_LDY_ZP, "Y")],
    ids=[
        "LDA Zero Page Can Load A Value Into The A Register",
        "LDX Zero Page Can Load A Value Into The X Register",
        "LDY Zero Page Can Load A Value Into The Y Register",
    ],
)
def test_load_register_zero_page(cpu, op_code, register):
    # Given
    expected_cycles = 3
    stored_value = 0x37
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0x42
    cpu.Memory[0x0042] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_ZPX, "A"), (OpCodes.INS_LDY_ZPX, "Y")],
    ids=[
        "LDA Zero Page With X Offset Can Load A Value Into The A Register",
        "LDY Zero Page With X Offset Can Load A Value Into The Y Register",
    ],
)
def test_load_register_zero_page_x_offset(cpu, op_code, register):
    # Given
    expected_cycles = 4
    stored_value = 0x37
    cpu.X = 5
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0x42
    cpu.Memory[0x0047] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDX_ZPY, "X")],
    ids=["LDY Zero Page With Y Offset Can Load A Value Into The X Register"],
)
def test_load_register_zero_page_y_offset(cpu, op_code, register):
    # Given
    expected_cycles = 4
    stored_value = 0x37
    cpu.Y = 5
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0x42
    cpu.Memory[0x0047] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_ABS, "A"), (OpCodes.INS_LDX_ABS, "X"), (OpCodes.INS_LDY_ABS, "Y")],
    ids=[
        "LDA Absolute Can Load A Value Into The A Register",
        "LDX Absolute Can Load A Value Into The X Register",
        "LDY Absolute Can Load A Value Into The Y Register",
    ],
)
def test_load_register_absolute(cpu, op_code, register):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    expected_cycles = 4
    stored_value = 0x37
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0x80
    cpu.Memory[0xFFFE] = 0x44  # 0x4480
    cpu.Memory[0x4480] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_ABSX, "A"), (OpCodes.INS_LDY_ABSX, "Y")],
    ids=[
        "LDA Absolute With X Offset Can Load A Value Into The A Register",
        "LDY Absolute With X Offset Can Load A Value Into The Y Register",
    ],
)
def test_load_register_absolute_x_offset(cpu, op_code, register):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    cpu.X = 1
    expected_cycles = 4
    stored_value = 0x37
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0x80
    cpu.Memory[0xFFFE] = 0x44  # 0x4481
    cpu.Memory[0x4481] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_ABSY, "A"), (OpCodes.INS_LDX_ABSY, "X")],
    ids=[
        "LDA Absolute With Y Offset Can Load A Value Into The A Register",
        "LDA Absolute With Y Offset Can Load A Value Into The X Register",
    ],
)
def test_load_register_absolute_y_offset(cpu, op_code, register):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    cpu.Y = 1
    expected_cycles = 4
    stored_value = 0x37
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0x80
    cpu.Memory[0xFFFE] = 0x44  # 0x4481
    cpu.Memory[0x4481] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_ABSY, "A"), (OpCodes.INS_LDX_ABSY, "X")],
    ids=[
        "LDA Absolute With Y Offset Can Load A Value Into The A Register When Crossing A Page",
        "LDA Absolute With Y Offset Can Load A Value Into The X Register When Crossing A Page",
    ],
)
def test_load_register_absolute_y_offset_when_crossing_page(cpu, op_code, register):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    cpu.Y = 0x1
    expected_cycles = 5
    stored_value = 0x37
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0xFF
    cpu.Memory[0xFFFE] = 0x44  # 0x44FF
    cpu.Memory[0x4500] = stored_value  # 0x44FF+0x1 crosses page boundary!
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


@pytest.mark.parametrize(
    "op_code,register",
    [(OpCodes.INS_LDA_ABSX, "A"), (OpCodes.INS_LDY_ABSX, "Y")],
    ids=[
        "LDA Absolute With X Offset Can Load A Value Into The A Register When Crossing A Page",
        "LDA Absolute With X Offset Can Load A Value Into The Y Register When Crossing A Page",
    ],
)
def test_load_register_absolute_x_offset_when_crossing_page(cpu, op_code, register):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    cpu.X = 0x1
    expected_cycles = 5
    stored_value = 0x37
    cpu.Memory[0xFFFC] = op_code
    cpu.Memory[0xFFFD] = 0xFF
    cpu.Memory[0xFFFE] = 0x44  # 0x44FF
    cpu.Memory[0x4500] = stored_value  # 0x44FF+0x1 crosses page boundary!
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(getattr(cpu, register)).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


def test_the_cpu_does_nothing_when_we_execute_zero_cycles(cpu):
    # Given
    expected_cycles = 0

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(cycles_used).IsEqualTo(expected_cycles)


def test_the_cpu_can_execute_more_cycles_than_requested_if_required_by_the_instruction(cpu):
    # Given
    expected_cycles = 1
    cpu.Memory[0xFFFC] = OpCodes.INS_LDA_IM
    cpu.Memory[0xFFFD] = 0x84
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(cycles_used).IsEqualTo(expected_cycles + 1)


def test_load_register_immediate_can_affect_the_zero_flag(cpu):
    # Given
    expected_cycles = 2
    cpu.A = 0x44
    cpu.Memory[0xFFFC] = OpCodes.INS_LDA_IM
    cpu.Memory[0xFFFD] = 0x0
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsTruthy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


def test_load_register_zero_page_x_can_load_a_value_into_the_register_when_it_wraps(cpu):
    """LDAZeroPageXCanLoadAValueIntoTheARegisterWhenItWraps"""
    # Given
    expected_cycles = 4
    stored_value = 0x37
    cpu.X = 0xFF
    cpu.Memory[0xFFFC] = OpCodes.INS_LDA_ZPX
    cpu.Memory[0xFFFD] = 0x80
    cpu.Memory[0x007F] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(cpu.A).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


def test_load_register_indirect_x_can_load_a_value_into_the_register(cpu):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    expected_cycles = 6
    stored_value = 0x37
    cpu.X = 0x04
    cpu.Memory[0xFFFC] = OpCodes.INS_LDA_INDX
    cpu.Memory[0xFFFD] = 0x02
    cpu.Memory[0x0006] = 0x00  # 0x2 + 0x4
    cpu.Memory[0x0007] = 0x80
    cpu.Memory[0x8000] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(cpu.A).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


def test_load_register_indirect_y_can_load_a_value_into_the_register(cpu):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    expected_cycles = 5
    stored_value = 0x37
    cpu.Y = 0x04
    cpu.Memory[0xFFFC] = OpCodes.INS_LDA_INDY
    cpu.Memory[0xFFFD] = 0x02
    cpu.Memory[0x0002] = 0x00  # 0x2 + 0x4
    cpu.Memory[0x0003] = 0x80
    cpu.Memory[0x8004] = stored_value
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(cpu.A).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)


def test_load_register_indirect_y_can_load_a_value_into_the_register_when_it_crosses_a_page(cpu):
    # Given
    cpu.Flag.Z = cpu.Flag.N = True
    expected_cycles = 6
    stored_value = 0x37
    cpu.Y = 0x1
    cpu.Memory[0xFFFC] = OpCodes.INS_LDA_INDY
    cpu.Memory[0xFFFD] = 0x05
    cpu.Memory[0x0005] = 0xFF
    cpu.Memory[0x0006] = 0x80
    cpu.Memory[0x8100] = stored_value  # 0x80FF + 0x1
    cpu_copy = copy.copy(cpu)

    # When
    cycles_used = cpu.execute(expected_cycles)

    # Then
    AssertThat(cpu.A).IsEqualTo(stored_value)
    AssertThat(cycles_used).IsEqualTo(expected_cycles)
    AssertThat(cpu.Flag.Z).IsFalsy()
    AssertThat(cpu.Flag.N).IsFalsy()
    verify_unmodified_flags_from_loading_register(cpu, cpu_copy)
