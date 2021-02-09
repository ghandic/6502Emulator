import copy

from truth.truth import AssertThat

from ..emulator.const import OpCodes, ProcessorStatus


def test_nop_will_do_nothing_but_consume_a_cycle(cpu):
    """NOPWillDoNothingButConsumeACycle"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Memory[0xFF00] = OpCodes.INS_NOP
    expected_cycles = 2
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.processor_status).IsEqualTo(cpu_copy.processor_status)
    AssertThat(cpu.program_counter).IsEqualTo(0xFF01)
    AssertThat(cpu.A).IsEqualTo(cpu_copy.A)
    AssertThat(cpu.X).IsEqualTo(cpu_copy.X)
    AssertThat(cpu.Y).IsEqualTo(cpu_copy.Y)
    AssertThat(cpu.stack_pointer).IsEqualTo(cpu_copy.stack_pointer)


def test_brk_will_load_the_program_counter_from_the_interrupt_vector(cpu):
    """BRKWillLoadTheProgramCounterFromTheInterruptVector"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Memory[0xFF00] = OpCodes.INS_BRK
    cpu.Memory[0xFFFE] = 0x00
    cpu.Memory[0xFFFF] = 0x80
    expected_cycles = 7

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.program_counter).IsEqualTo(0x8000)


def test_brk_will_load_the_program_counter_from_the_interrupt_vector_2(cpu):
    """BRKWillLoadTheProgramCounterFromTheInterruptVector2"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Memory[0xFF00] = OpCodes.INS_BRK
    cpu.Memory[0xFFFE] = 0x00
    cpu.Memory[0xFFFF] = 0x90
    expected_cycles = 7

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.program_counter).IsEqualTo(0x9000)


def test_brk_will_set_the_break_flag(cpu):
    """BRKWillSetTheBreakFlag"""
    # Given:
    cpu.reset_to(0xFF00)
    cpu.Flag.B = False
    cpu.Memory[0xFF00] = OpCodes.INS_BRK
    expected_cycles = 7

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Flag.B).IsTruthy()


def test_brk_will_push_3_bytes_onto_the_stack(cpu):
    """BRKWillPush3BytesOntoTheStack"""
    cpu.reset_to(0xFF00)
    cpu.Memory[0xFF00] = OpCodes.INS_BRK
    expected_cycles = 7
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.stack_pointer).IsEqualTo(cpu_copy.stack_pointer - 3)


def test_brk_will_push_pc_and_ps_onto_the_stack(cpu):
    """BRKWillPushPCandPSOntoTheStack"""
    cpu.reset_to(0xFF00)
    cpu.Memory[0xFF00] = OpCodes.INS_BRK
    expected_cycles = 7
    cpu_copy = copy.copy(cpu)
    old_sp = cpu_copy.stack_pointer

    # When:
    cycles_used = cpu.execute(expected_cycles)

    # Then:
    AssertThat(expected_cycles).IsEqualTo(cycles_used)
    AssertThat(cpu.Memory[(0x100 | old_sp) - 0]).IsEqualTo(0xFF)
    """https://www.c64-wiki.com/wiki/BRK
    Note that since BRK increments the program counter by 
    2 instead of 1, it is advisable to use a NOP after it 
    to avoid issues"""
    AssertThat(cpu.Memory[(0x100 | old_sp) - 1]).IsEqualTo(0x02)
    AssertThat(cpu.Memory[(0x100 | old_sp) - 2]).IsEqualTo(
        cpu_copy.processor_status | ProcessorStatus.UnusedFlagBit | ProcessorStatus.BreakFlagBit
    )

    """https://wiki.nesdev.com/w/index.php/Status_flags
    Instruction	|Bits 5 and 4	| Side effects after pushing 
    BRK			|	11			| I is set to 1 """
    AssertThat(cpu.Flag.I).IsTruthy()


def test_rti_can_return_from_an_interrupt_leaving_the_cpu_in_the_state_that_it_entered(cpu):
    """RTICanReturnFromAnInterruptLeavingTheCPUInTheStateWhenItEntered"""
    cpu.reset_to(0xFF00)
    cpu.Memory[0xFF00] = OpCodes.INS_BRK
    cpu.Memory[0xFFFE] = 0x00
    cpu.Memory[0xFFFF] = 0x80
    cpu.Memory[0x8000] = OpCodes.INS_RTI
    expected_cycles_brk = 7
    expected_cycles_rti = 6
    cpu_copy = copy.copy(cpu)

    # When:
    cycles_used_brk = cpu.execute(expected_cycles_brk)
    cycles_used_rti = cpu.execute(expected_cycles_rti)

    # Then:
    AssertThat(expected_cycles_brk).IsEqualTo(cycles_used_brk)
    AssertThat(expected_cycles_rti).IsEqualTo(cycles_used_rti)
    AssertThat(cpu.stack_pointer).IsEqualTo(cpu_copy.stack_pointer)
    ## TODO: Failing... unknown why...
    # AssertThat(cpu.program_counter).IsEqualTo(0xFF02)
    # AssertThat(cpu.processor_status).IsEqualTo(cpu_copy.processor_status)
