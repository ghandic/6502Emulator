import copy

from truth.truth import AssertThat

from ..emulator.const import OpCodes


def test_clc_will_clear_the_carry_flag(cpu):
    """CLCWillClearTheCarryFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.C = True
    cpu.Memory[0xFF00] = OpCodes.INS_CLC
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.C).IsFalsy()
    AssertThat(cpu.Flag.Z).IsEqualTo(cpu_copy.Flag.Z)
    AssertThat(cpu.Flag.I).IsEqualTo(cpu_copy.Flag.I)
    AssertThat(cpu.Flag.D).IsEqualTo(cpu_copy.Flag.D)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.V).IsEqualTo(cpu_copy.Flag.V)
    AssertThat(cpu.Flag.N).IsEqualTo(cpu_copy.Flag.N)


def test_sec_will_clear_the_carry_flag(cpu):
    """SECWillSetTheCarryFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.C = False
    cpu.Memory[0xFF00] = OpCodes.INS_SEC
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.C).IsTruthy()
    AssertThat(cpu.Flag.Z).IsEqualTo(cpu_copy.Flag.Z)
    AssertThat(cpu.Flag.I).IsEqualTo(cpu_copy.Flag.I)
    AssertThat(cpu.Flag.D).IsEqualTo(cpu_copy.Flag.D)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.V).IsEqualTo(cpu_copy.Flag.V)
    AssertThat(cpu.Flag.N).IsEqualTo(cpu_copy.Flag.N)


def test_cld_will_clear_the_decimal_flag(cpu):
    """CLDWillClearTheDecimalFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.D = True
    cpu.Memory[0xFF00] = OpCodes.INS_CLD
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.D).IsFalsy()
    AssertThat(cpu.Flag.Z).IsEqualTo(cpu_copy.Flag.Z)
    AssertThat(cpu.Flag.I).IsEqualTo(cpu_copy.Flag.I)
    AssertThat(cpu.Flag.C).IsEqualTo(cpu_copy.Flag.C)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.V).IsEqualTo(cpu_copy.Flag.V)
    AssertThat(cpu.Flag.N).IsEqualTo(cpu_copy.Flag.N)


def test_sed_will_clear_the_decimal_flag(cpu):
    """SEDWillSetTheDecimalFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.D = False
    cpu.Memory[0xFF00] = OpCodes.INS_SED
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.D).IsTruthy()
    AssertThat(cpu.Flag.Z).IsEqualTo(cpu_copy.Flag.Z)
    AssertThat(cpu.Flag.I).IsEqualTo(cpu_copy.Flag.I)
    AssertThat(cpu.Flag.C).IsEqualTo(cpu_copy.Flag.C)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.V).IsEqualTo(cpu_copy.Flag.V)
    AssertThat(cpu.Flag.N).IsEqualTo(cpu_copy.Flag.N)


def test_cli_will_clear_the_interrupt_flag(cpu):
    """CLIWillClearTheInterruptFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.I = True
    cpu.Memory[0xFF00] = OpCodes.INS_CLI
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.I).IsFalsy()
    AssertThat(cpu.Flag.Z).IsEqualTo(cpu_copy.Flag.Z)
    AssertThat(cpu.Flag.D).IsEqualTo(cpu_copy.Flag.D)
    AssertThat(cpu.Flag.C).IsEqualTo(cpu_copy.Flag.C)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.V).IsEqualTo(cpu_copy.Flag.V)
    AssertThat(cpu.Flag.N).IsEqualTo(cpu_copy.Flag.N)


def test_sei_will_clear_the_interrupt_flag(cpu):
    """SEIWillSetTheInterruptFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.I = False
    cpu.Memory[0xFF00] = OpCodes.INS_SEI
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.I).IsTruthy()
    AssertThat(cpu.Flag.Z).IsEqualTo(cpu_copy.Flag.Z)
    AssertThat(cpu.Flag.D).IsEqualTo(cpu_copy.Flag.D)
    AssertThat(cpu.Flag.C).IsEqualTo(cpu_copy.Flag.C)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.V).IsEqualTo(cpu_copy.Flag.V)
    AssertThat(cpu.Flag.N).IsEqualTo(cpu_copy.Flag.N)


def test_clv_will_clear_the_overflow_flag(cpu):
    """CLVWillClearTheOverflowFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.V = True
    cpu.Memory[0xFF00] = OpCodes.INS_CLV
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.V).IsFalsy()
    AssertThat(cpu.Flag.Z).IsEqualTo(cpu_copy.Flag.Z)
    AssertThat(cpu.Flag.D).IsEqualTo(cpu_copy.Flag.D)
    AssertThat(cpu.Flag.C).IsEqualTo(cpu_copy.Flag.C)
    AssertThat(cpu.Flag.B).IsEqualTo(cpu_copy.Flag.B)
    AssertThat(cpu.Flag.I).IsEqualTo(cpu_copy.Flag.I)
    AssertThat(cpu.Flag.N).IsEqualTo(cpu_copy.Flag.N)
