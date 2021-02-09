from truth.truth import AssertThat

from ..emulator.c_types import Byte

test_program = """
; TestPrg

* = $1000

lda #$FF

start
sta $90
sta $8000
eor #$CC
jmp start
"""

test_program = [Byte(x) for x in [0x00, 0x10, 0xA9, 0xFF, 0x85, 0x90, 0x8D, 0x00, 0x80, 0x49, 0xCC, 0x4C, 0x02, 0x10]]


def test_load_program_into_the_correct_area_of_memory(cpu):
    # when:
    cpu.load_program(test_program, len(test_program))

    # then:
    AssertThat(cpu.Memory[0x0FFF]).IsEqualTo(Byte(0x0))
    AssertThat(cpu.Memory[0x1000]).IsEqualTo(Byte(0xA9))
    AssertThat(cpu.Memory[0x1001]).IsEqualTo(Byte(0xFF))
    AssertThat(cpu.Memory[0x1002]).IsEqualTo(Byte(0x85))
    # ...
    AssertThat(cpu.Memory[0x1009]).IsEqualTo(Byte(0x4C))
    AssertThat(cpu.Memory[0x100A]).IsEqualTo(Byte(0x02))
    AssertThat(cpu.Memory[0x100B]).IsEqualTo(Byte(0x10))
    AssertThat(cpu.Memory[0x100C]).IsEqualTo(Byte(0x0))


def test_load_program_and_execute_it(cpu):
    # when:
    start_address = cpu.load_program(test_program, len(test_program))
    cpu.program_counter = start_address

    # then:
    clock = 1000
    while clock > 0:
        clock -= cpu.execute(1)


# TODO: LoadThe6502TestPrg - unsure on how to read in as binary
# def test_load_6502_program_and_execute_it(cpu):
#     # when:
#     program = []
#     with open(Path(__file__).parent / "6502_functional_test.bin", "rb") as f:
#         data = [Byte(x) for x in bytearray(f.read())]

#     start_address = cpu.load_program(program, len(test_program))
#     cpu.program_counter = 0x400
#     while True:
#         cpu.execute(1)
