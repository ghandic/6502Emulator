from typing import List

from .c_types import Byte, SByte, Word, s32, u32
from .const import OpCodes, ProcessorStatus, StatusFlags
from .utils import switch


class Memory(object):
    def __init__(self):
        self.max_memory = 1024 * 64
        self.data = [Byte(0)] * self.max_memory

    def __getitem__(self, address: u32) -> Byte:
        assert 0 <= int(address) <= self.max_memory
        return Byte(self.data[int(address)])

    def __setitem__(self, address: u32, value: Byte) -> Byte:
        assert 0 <= int(address) <= self.max_memory
        self.data[int(address)] = Byte(value)
        return self.data[address]


class CPU(object):
    def __init__(self):
        self.program_counter: Word = Word(0xFFFC)
        self.stack_pointer: Byte = Byte(0xFF)
        self.processor_status: Byte = Byte(0xFF)
        self.cycles: s32 = 0

        self.A: Byte = Byte(0)
        self.X: Byte = Byte(0)
        self.Y: Byte = Byte(0)

        self.Flag: StatusFlags = StatusFlags(Byte(0), Byte(0), Byte(0), Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))
        self.Memory: Memory = Memory()

    def __repr__(self) -> str:
        """Makes string representation of CPU:  the registers, program counter etc"""
        return f"A: {self.A} X: {self.X} Y: {self.Y}\nPC: {self.program_counter} SP: {self.stack_pointer}\nPS: {self.processor_status}\n"

    def reset(self) -> None:
        self.__init__()

    def reset_to(self, reset_vector: Word) -> None:
        self.reset()
        self.program_counter = reset_vector

    @property
    def sp_to_address(self) -> Word:
        return Word(0x100 | self.stack_pointer)

    def __get_register(self, register: str) -> Byte:
        assert register in ["A", "X", "Y"]
        return getattr(self, register)

    def __set_register(self, register: str, value: Word) -> Byte:
        assert register in ["A", "X", "Y"]
        return setattr(self, register, value)

    def fetch_byte(self) -> Byte:
        data = self.Memory[self.program_counter]
        self.program_counter += 1
        self.cycles -= 1
        return Byte(data)

    def fetch_sbyte(self) -> SByte:
        return SByte(self.fetch_byte())

    def fetch_word(self) -> Word:
        # 6502 is little endian
        data = self.Memory[self.program_counter]
        self.program_counter += 1

        data |= self.Memory[self.program_counter] << 8
        self.program_counter += 1
        self.cycles -= 2
        return Word(data)

    def read_byte(self, address: Word) -> Byte:
        data = self.Memory[address]
        self.cycles -= 1
        return Byte(data)

    def read_word(self, address: Word) -> Byte:
        low_byte = self.read_byte(address)
        high_byte = self.read_byte(address + 1)
        return Word(low_byte | (high_byte << 8))

    def write_byte(self, address: Word, value: Byte) -> None:
        self.Memory[address] = value
        self.cycles -= 1

    def write_word(self, address: Word, value: Word) -> None:
        self.Memory[address] = value & 0xFF
        self.Memory[address + 1] = value >> 8
        self.cycles -= 2

    def push_byte_onto_stack(self, value: Byte) -> None:
        self.Memory[self.sp_to_address] = value
        self.cycles -= 1
        self.stack_pointer -= 1
        self.cycles -= 1

    def push_word_onto_stack(self, value: Word) -> None:
        self.write_byte(address=self.sp_to_address, value=value >> 8)
        self.stack_pointer -= 1
        self.write_byte(address=self.sp_to_address, value=value & 0xFF)
        self.stack_pointer -= 1

    def push_pc_onto_stack(self) -> None:
        self.push_word_onto_stack(self.program_counter)

    def push_pc_minus_1_onto_stack(self) -> None:
        self.push_word_onto_stack(self.program_counter - 1)

    def push_pc_plus_1_onto_stack(self) -> None:
        self.push_word_onto_stack(self.program_counter + 1)

    def pop_byte_from_stack(self) -> Byte:
        self.stack_pointer += 1
        self.cycles -= 1
        value = self.Memory[self.sp_to_address]
        self.cycles -= 1
        return value

    def pop_word_from_stack(self) -> Word:
        value = self.read_word(self.sp_to_address + 1)
        self.stack_pointer += 2
        self.cycles -= 1
        return Word(value)

    def set_zero_and_negative_flags(self, register: str) -> None:
        _register = self.__get_register(register)
        self.Flag.Z = int(_register == 0)
        self.Flag.N = int((_register & ProcessorStatus.NegativeFlagBit) > 0)

    def address_zero_page(self) -> Word:
        """Addressing mode - Zero page"""
        zero_page_address = self.fetch_byte()
        return zero_page_address

    def address_zero_page_x_offset(self) -> Word:
        """Addressing mode - Zero page with X offset"""
        zero_page_address = self.fetch_byte()
        # TODO: Need to fix zero_page_address and X, Y, A etc to 256 bit...
        zero_page_address = zero_page_address + self.X
        self.cycles -= 1
        return zero_page_address

    def address_zero_page_y_offset(self) -> Word:
        """Addressing mode - Zero page with Y offset"""
        zero_page_address = self.fetch_byte()
        zero_page_address += self.Y
        self.cycles -= 1
        return zero_page_address

    def address_absolute(self) -> Word:
        """Addressing mode - Absolute"""
        absolute_address = self.fetch_word()
        return absolute_address

    def address_absolute_x_offset(self) -> Word:
        """Addressing mode - Absolute with X offset"""
        absolute_address = self.fetch_word()
        absolute_address_x = absolute_address + self.X
        crossed_page_boundary: bool = (absolute_address ^ absolute_address_x) >> 8
        if crossed_page_boundary:
            self.cycles -= 1
        return absolute_address_x

    def address_absolute_x_offset_5(self) -> Word:
        """Addressing mode - Absolute with X offset
            - Always takes a cycle for the X page boundary)
            - See "STA Absolute,X"
        """
        absolute_address = self.fetch_word()
        absolute_address_x = absolute_address + self.X
        self.cycles -= 1
        return absolute_address_x

    def address_absolute_y_offset(self) -> Word:
        """Addressing mode - Absolute with Y offset"""
        absolute_address = self.fetch_word()
        absolute_address_y = absolute_address + self.Y
        crossed_page_boundary: bool = (absolute_address ^ absolute_address_y) >> 8
        if crossed_page_boundary:
            self.cycles -= 1
        return absolute_address_y

    def address_absolute_y_offset_5(self) -> Word:
        """Addressing mode - Absolute with Y offset
            - Always takes a cycle for the Y page boundary)
            - See "STA Absolute,Y"
        """
        absolute_address = self.fetch_word()
        absolute_address_y = absolute_address + self.Y
        self.cycles -= 1
        return absolute_address_y

    def address_indirect_x_offset(self) -> Word:
        """Addressing mode - Indirect X | Indexed Indirect"""
        zp_address = self.fetch_byte()
        zp_address += self.X
        self.cycles -= 1
        effective_address = self.read_word(zp_address)
        return effective_address

    def address_indirect_y_offset(self) -> Word:
        """Addressing mode - Indirect Y | Indirect Indexed"""
        zp_address = self.fetch_byte()
        effective_address = self.read_word(zp_address)
        effective_address_y = effective_address + self.Y
        crossed_page_boundary: bool = (effective_address ^ effective_address_y) >> 8
        if crossed_page_boundary:
            self.cycles -= 1
        return effective_address_y

    def address_indirect_x_offset_6(self) -> Word:
        """Addressing mode - Indirect Y | Indirect Indexed
            - Always takes a cycle for the Y page boundary)
            -See "STA (Indirect,Y)"
        """
        zp_address = self.fetch_byte()
        effective_address = self.read_word(zp_address)
        effective_address_y = effective_address + self.Y
        self.cycles -= 1
        return effective_address_y

    def load_program(self, program: List[Byte], num_bytes: u32) -> Word:
        """Returns the address that the program was loading into, or 0 if no program"""
        load_address: Word = 0
        if program and num_bytes:
            at: u32 = 0
            low = program[at]
            at += 1
            high = program[at] << 8
            at += 1
            load_address = low | high
            for i in range(load_address, load_address + num_bytes - 2):
                self.Memory[i] = program[at]
                at += 1
        return load_address

    def __load_register(self, address: Word, register: str) -> None:
        """Load a Register with the value from the memory address"""

        _register_value = self.read_byte(address)
        self.__set_register(register, _register_value)
        self.set_zero_and_negative_flags(register)

    def __anda(self, address: Word) -> None:
        """And the A Register with the value from the memory address"""
        self.A &= self.read_byte(address)
        self.set_zero_and_negative_flags("A")

    def __ora(self, address: Word) -> None:
        """Or the A Register with the value from the memory address"""
        self.A |= self.read_byte(address)
        self.set_zero_and_negative_flags("A")

    def __eora(self, address: Word) -> None:
        """Eor the A Register with the value from the memory address"""
        self.A ^= self.read_byte(address)
        self.set_zero_and_negative_flags("A")

    def __branch_if(self, test: bool, expected: bool) -> None:
        """Conditional branch"""
        offset = self.fetch_sbyte()
        if test == expected:
            program_counter_old = self.program_counter
            self.program_counter += offset
            self.cycles -= 1

            page_changed: bool = (self.program_counter >> 8) != (program_counter_old >> 8)
            if page_changed:
                self.cycles -= 1

    def __add_with_carry(self, operand: Byte) -> None:
        """Do add with carry given the the operand"""
        assert not self.Flag.D, "Haven't handled decimal mode!"
        are_sign_bits_the_same: bool = not ((self.A ^ operand) & ProcessorStatus.NegativeFlagBit)
        _sum = self.A
        _sum += operand
        _sum += self.Flag.C
        self.A = _sum & 0xFF
        self.set_zero_and_negative_flags("A")
        self.Flag.C = _sum > 0xFF
        self.Flag.V = are_sign_bits_the_same and ((self.A ^ operand) & ProcessorStatus.NegativeFlagBit)

    def __subtract_with_carry(self, operand: Byte) -> None:
        """Do subtract with carry given the the operand"""
        self.__add_with_carry(~operand)

    def __register_compare(self, operand: Byte, register_value: Byte) -> None:
        """Sets the processor status for a CMP/CPX/CPY instruction"""
        temp = register_value - operand
        self.Flag.N = (temp & ProcessorStatus.NegativeFlagBit) > 0
        self.Flag.Z = register_value == operand
        self.Flag.C = register_value >= operand

    def __arithmetic_shift_left(self, operand: Byte) -> Byte:
        """Arithmetic shift left"""
        self.Flag.C = (operand & ProcessorStatus.NegativeFlagBit) > 0
        result = operand << 1
        # TODO: unsure how this would work?
        self.set_zero_and_negative_flags(result)
        self.cycles -= 1
        return result

    def __logical_shift_right(self, operand: Byte) -> Byte:
        """Logical shift right"""
        self.Flag.C = (operand & ProcessorStatus.ZeroBit) > 0
        result = operand >> 1
        # TODO: unsure how this would work?
        self.set_zero_and_negative_flags(result)
        self.cycles -= 1
        return result

    def __rotate_left(self, operand: Byte) -> Byte:
        """Rotate left"""
        new_bit_0 = ProcessorStatus.ZeroBit if self.Flag.C else 0
        self.Flag.C = int((operand & ProcessorStatus.NegativeFlagBit) > 0)
        operand = operand << 1
        operand |= new_bit_0
        self.cycles -= 1
        return operand

    def __rotate_right(self, operand: Byte) -> Byte:
        """Rotate left"""
        old_bit_0 = int((operand & ProcessorStatus.ZeroBit) > 0)
        operand = operand >> 1
        if self.Flag.C:
            operand |= ProcessorStatus.NegativeFlagBit
        self.cycles -= 1
        self.Flag.C = old_bit_0
        # TODO: unsure how this would work?
        self.set_zero_and_negative_flags(operand)
        return operand

    def __increment_at(self, address: Word) -> None:
        value = self.read_byte(address)
        value += 1
        self.cycles -= 1
        self.write_byte(address, value)
        # TODO: unsure how this would work?
        self.set_zero_and_negative_flags(value)

    def __decrement_at(self, address: Word) -> None:
        value = self.read_byte(address)
        value -= 1
        self.cycles -= 1
        self.write_byte(address, value)
        # TODO: unsure how this would work?
        self.set_zero_and_negative_flags(value)

    def __push_processor_status_onto_stack(self) -> None:
        """Push Processor status onto the stack - Setting bits 4 & 5 on the stack"""
        ps_stack = self.processor_status | ProcessorStatus.BreakFlagBit | ProcessorStatus.UnusedFlagBit
        self.push_byte_onto_stack(ps_stack)

    def __pop_processor_status_from_stack(self) -> None:
        """Pop Processor status from the stack - Clearing bits 4 & 5 (Break & Unused)"""
        self.pop_byte_from_stack()
        self.Flag.B = int(False)
        self.Flag.U = int(False)

    def execute(self, cycles: bytes) -> s32:
        """TODO: Return the number of cycles that were used"""
        num_cycles_requested = cycles
        self.cycles = cycles
        while self.cycles > 0:
            instruction = self.fetch_byte()
            for case in switch(instruction):
                if case(OpCodes.INS_AND_IM):
                    self.A &= self.fetch_byte()
                    self.set_zero_and_negative_flags("A")
                    break
                if case(OpCodes.INS_ORA_IM):
                    self.A |= self.fetch_byte()
                    self.set_zero_and_negative_flags("A")
                    break
                if case(OpCodes.INS_EOR_IM):
                    self.A ^= self.fetch_byte()
                    self.set_zero_and_negative_flags("A")
                    break
                if case(OpCodes.INS_AND_ZP):
                    address = self.address_zero_page()
                    self.__anda(address)
                    break
                if case(OpCodes.INS_ORA_ZP):
                    address = self.address_zero_page()
                    self.__ora(address)
                    break
                if case(OpCodes.INS_EOR_ZP):
                    address = self.address_zero_page()
                    self.__eora(address)
                    break
                if case(OpCodes.INS_AND_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.__anda(address)
                    break
                if case(OpCodes.INS_ORA_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.ora(address)
                    break
                if case(OpCodes.INS_EOR_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.__eora(address)
                    break

                if case(OpCodes.INS_AND_ABS):
                    address = self.address_absolute()
                    self.__anda(address)
                    break
                if case(OpCodes.INS_ORA_ABS):
                    address = self.address_absolute()
                    self.__ora(address)
                    break
                if case(OpCodes.INS_EOR_ABS):
                    address = self.address_absolute()
                    self.__eora(address)
                    break

                if case(OpCodes.INS_AND_ABSX):
                    address = self.address_absolute_x_offset()
                    self.__anda(address)
                    break
                if case(OpCodes.INS_ORA_ABSX):
                    address = self.address_absolute_x_offset()
                    self.__ora(address)
                    break
                if case(OpCodes.INS_EOR_ABSX):
                    address = self.address_absolute_x_offset()
                    self.__eora(address)
                    break

                if case(OpCodes.INS_AND_ABSY):
                    address = self.address_absolute_y_offset()
                    self.__anda(address)
                    break
                if case(OpCodes.INS_ORA_ABSY):
                    address = self.address_absolute_y_offset()
                    self.__ora(address)
                    break
                if case(OpCodes.INS_EOR_ABSY):
                    address = self.address_absolute_y_offset()
                    self.__eora(address)
                    break

                if case(OpCodes.INS_AND_INDX):
                    address = self.address_indirect_x_offset()
                    self.__anda(address)
                    break
                if case(OpCodes.INS_ORA_INDX):
                    address = self.address_indirect_x_offset()
                    self.__ora(address)
                    break
                if case(OpCodes.INS_EOR_INDX):
                    address = self.address_indirect_x_offset()
                    self.__eora(address)
                    break

                if case(OpCodes.INS_AND_INDY):
                    address = self.address_indirect_y_offset()
                    self.__anda(address)
                    break
                if case(OpCodes.INS_ORA_INDY):
                    address = self.address_indirect_y_offset()
                    self.__ora(address)
                    break
                if case(OpCodes.INS_EOR_INDY):
                    address = self.address_indirect_y_offset()
                    self.__eora(address)
                    break

                if case(OpCodes.INS_BIT_ZP):
                    address = self.address_zero_page()
                    value = self.read_byte(address)
                    self.Flag.Z = not (self.A & value)
                    self.Flag.N = (value & ProcessorStatus.NegativeFlagBit) != 0
                    self.Flag.V = (value & ProcessorStatus.OverflowFlagBit) != 0
                    break
                if case(OpCodes.INS_BIT_ABS):
                    address = self.address_absolute()
                    value = self.read_byte(address)
                    self.Flag.Z = not (self.A & value)
                    self.Flag.N = (value & ProcessorStatus.NegativeFlagBit) != 0
                    self.Flag.V = (value & ProcessorStatus.OverflowFlagBit) != 0
                    break

                if case(OpCodes.INS_LDA_IM):
                    self.__set_register("A", self.fetch_byte())
                    self.set_zero_and_negative_flags("A")
                    break
                if case(OpCodes.INS_LDX_IM):
                    self.__set_register("X", self.fetch_byte())
                    self.set_zero_and_negative_flags("X")
                    break
                if case(OpCodes.INS_LDY_IM):
                    self.__set_register("Y", self.fetch_byte())
                    self.set_zero_and_negative_flags("Y")
                    break

                if case(OpCodes.INS_LDA_ZP):
                    address = self.address_zero_page()
                    self.__load_register(address, "A")
                    break
                if case(OpCodes.INS_LDX_ZP):
                    address = self.address_zero_page()
                    self.__load_register(address, "X")
                    break
                if case(OpCodes.INS_LDY_ZP):
                    address = self.address_zero_page()
                    self.__load_register(address, "Y")
                    break

                if case(OpCodes.INS_LDX_ZPY):
                    address = self.address_zero_page_y_offset()
                    self.__load_register(address, "X")
                    break

                if case(OpCodes.INS_LDA_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.__load_register(address, "A")
                    break
                if case(OpCodes.INS_LDY_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.__load_register(address, "Y")
                    break

                if case(OpCodes.INS_LDA_ABS):
                    address = self.address_absolute()
                    self.__load_register(address, "A")
                    break
                if case(OpCodes.INS_LDX_ABS):
                    address = self.address_absolute()
                    self.__load_register(address, "X")
                    break
                if case(OpCodes.INS_LDY_ABS):
                    address = self.address_absolute()
                    self.__load_register(address, "Y")
                    break

                if case(OpCodes.INS_LDA_ABSX):
                    address = self.address_absolute_x_offset()
                    self.__load_register(address, "A")
                    break
                if case(OpCodes.INS_LDY_ABSX):
                    address = self.address_absolute_x_offset()
                    self.__load_register(address, "Y")
                    break

                if case(OpCodes.INS_LDA_ABSY):
                    address = self.address_absolute_y_offset()
                    self.__load_register(address, "A")
                    break
                if case(OpCodes.INS_LDX_ABSY):
                    address = self.address_absolute_y_offset()
                    self.__load_register(address, "X")
                    break

                if case(OpCodes.INS_LDA_INDX):
                    address = self.address_indirect_x_offset()
                    self.__load_register(address, "A")
                    break
                if case(OpCodes.INS_STA_INDX):
                    address = self.address_indirect_x_offset()
                    self.write_byte(address, self.A)
                    break
                if case(OpCodes.INS_LDA_INDY):
                    address = self.address_indirect_y_offset()
                    self.__load_register(address, "A")
                    break
                if case(OpCodes.INS_STA_INDY):
                    address = self.address_indirect_y_offset()
                    self.write_byte(address, self.A)
                    break
                if case(OpCodes.INS_STA_ZP):
                    address = self.address_zero_page()
                    self.write_byte(address, self.A)
                    break
                if case(OpCodes.INS_STX_ZP):
                    address = self.address_zero_page()
                    self.write_byte(address, self.X)
                    break
                if case(OpCodes.INS_STX_ZPY):
                    address = self.address_zero_page_y_offset()
                    self.write_byte(address, self.X)
                    break
                if case(OpCodes.INS_STY_ZP):
                    address = self.address_zero_page()
                    self.write_byte(address, self.Y)
                    break
                if case(OpCodes.INS_STA_ABS):
                    address = self.address_absolute()
                    self.write_byte(address, self.A)
                    break
                if case(OpCodes.INS_STX_ABS):
                    address = self.address_absolute()
                    self.write_byte(address, self.X)
                    break
                if case(OpCodes.INS_STY_ABS):
                    address = self.address_absolute()
                    self.write_byte(address, self.Y)
                    break
                if case(OpCodes.INS_STA_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.write_byte(address, self.A)
                    break
                if case(OpCodes.INS_STY_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.write_byte(address, self.Y)
                    break
                if case(OpCodes.INS_STA_ABSX):
                    address = self.address_absolute_x_offset_5()
                    self.write_byte(address, self.A)
                    break
                if case(OpCodes.INS_STA_ABSY):
                    address = self.address_absolute_y_offset_5()
                    self.write_byte(address, self.A)
                    break
                if case(OpCodes.INS_JSR):
                    sub_address = self.fetch_word()
                    self.push_pc_minus_1_onto_stack()
                    self.program_counter = sub_address
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_RTS):
                    return_address = self.pop_word_from_stack()
                    self.program_counter = return_address + 1
                    self.cycles -= 2
                    break
                """TODO:
                An original 6502 has does not correctly fetch the target
                address if the indirect vector falls on a page boundary
                ( e.g.$xxFF where xx is any value from $00 to $FF ).
                In this case fetches the LSB from $xxFF as expected but
                takes the MSB from $xx00.This is fixed in some later chips
                like the 65SC02 so for compatibility always ensure the
                indirect vector is not at the end of the page."""
                if case(OpCodes.INS_JMP_ABS):
                    address = self.address_absolute()
                    self.program_counter = address
                    break
                if case(OpCodes.INS_JMP_IND):
                    address = self.address_absolute()
                    address = self.read_word(address)
                    self.program_counter = address
                    break
                if case(OpCodes.INS_TSX):
                    self.X = self.stack_pointer
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("X")
                    break
                if case(OpCodes.INS_TXS):
                    self.stack_pointer = self.X
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_PHA):
                    self.push_byte_onto_stack(self.A)
                    break
                if case(OpCodes.INS_PLA):
                    self.A = self.pop_byte_from_stack()
                    self.set_zero_and_negative_flags("A")
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_PHP):
                    self.__push_processor_status_onto_stack()
                    break
                if case(OpCodes.INS_PLP):
                    self.__pop_processor_status_from_stack()
                    break
                if case(OpCodes.INS_TAX):
                    self.X = self.A
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("X")
                    break
                if case(OpCodes.INS_TAY):
                    self.Y = self.A
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("Y")
                    break
                if case(OpCodes.INS_TXA):
                    self.A = self.X
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("A")
                    break
                if case(OpCodes.INS_TYA):
                    self.A = self.Y
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("A")
                    break
                if case(OpCodes.INS_INX):
                    self.X += 1
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("X")
                    break
                if case(OpCodes.INS_INY):
                    self.Y += 1
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("Y")
                    break
                if case(OpCodes.INS_DEX):
                    self.X -= 1
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("X")
                    break
                if case(OpCodes.INS_DEY):
                    self.Y -= 1
                    self.cycles -= 1
                    self.set_zero_and_negative_flags("Y")
                    break
                if case(OpCodes.INS_DEC_ZP):
                    address = self.address_zero_page()
                    self.__decrement_at(address)
                    break
                if case(OpCodes.INS_DEC_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.__decrement_at(address)
                    break
                if case(OpCodes.INS_DEC_ABS):
                    address = self.address_absolute()
                    self.__decrement_at(address)
                    break
                if case(OpCodes.INS_DEC_ABSX):
                    address = self.address_absolute_x_offset_5()
                    self.__decrement_at(address)
                    break
                if case(OpCodes.INS_INC_ZP):
                    address = self.address_zero_page()
                    self.__increment_at(address)
                    break
                if case(OpCodes.INS_INC_ZPX):
                    address = self.address_zero_page_x_offset()
                    self.__increment_at(address)
                    break
                if case(OpCodes.INS_INC_ABS):
                    address = self.address_absolute()
                    self.__increment_at(address)
                    break
                if case(OpCodes.INS_INC_ABSX):
                    address = self.address_absolute_x_offset_5()
                    self.__increment_at(address)
                    break
                if case(OpCodes.INS_BEQ):
                    self.__branch_if(self.Flag.Z, True)
                    break
                if case(OpCodes.INS_BNE):
                    self.__branch_if(self.Flag.Z, False)
                    break
                if case(OpCodes.INS_BCS):
                    self.__branch_if(self.Flag.C, True)
                    break
                if case(OpCodes.INS_BCC):
                    self.__branch_if(self.Flag.C, False)
                    break
                if case(OpCodes.INS_BMI):
                    self.__branch_if(self.Flag.N, True)
                    break
                if case(OpCodes.INS_BPL):
                    self.__branch_if(self.Flag.N, False)
                    break
                if case(OpCodes.INS_BVC):
                    self.__branch_if(self.Flag.V, False)
                    break
                if case(OpCodes.INS_BVS):
                    self.__branch_if(self.Flag.V, True)
                    break
                if case(OpCodes.INS_CLC):
                    self.Flag.C = int(False)
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_SEC):
                    self.Flag.C = int(True)
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_CLD):
                    self.Flag.D = int(False)
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_SED):
                    self.Flag.D = int(True)
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_CLI):
                    self.Flag.I = int(False)
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_SEI):
                    self.Flag.I = int(True)
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_CLV):
                    self.Flag.V = int(False)
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_NOP):
                    self.cycles -= 1
                    break
                if case(OpCodes.INS_ADC_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_ADC_ABSX):
                    address = self.address_absolute_x_offset()
                    operand = self.read_byte(address)
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_ADC_ABSY):
                    address = self.address_absolute_y_offset()
                    operand = self.read_byte(address)
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_ADC_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_ADC_ZPX):
                    address = self.address_zero_page_x_offset()
                    operand = self.read_byte(address)
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_ADC_INDX):
                    address = self.address_indirect_x_offset()
                    operand = self.read_byte(address)
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_ADC_INDY):
                    address = self.address_indirect_y_offset()
                    operand = self.read_byte(address)
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_ADC):
                    operand = self.fetch_byte()
                    self.__add_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC):
                    operand = self.fetch_byte()
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC_ZPX):
                    address = self.address_zero_page_x_offset()
                    operand = self.read_byte(address)
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC_ABSX):
                    address = self.address_absolute_x_offset()
                    operand = self.read_byte(address)
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC_ABSY):
                    address = self.address_absolute_y_offset()
                    operand = self.read_byte(address)
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC_INDX):
                    address = self.address_indirect_x_offset()
                    operand = self.read_byte(address)
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_SBC_INDY):
                    address = self.address_indirect_y_offset()
                    operand = self.read_byte(address)
                    self.__subtract_with_carry(operand)
                    break
                if case(OpCodes.INS_CPX):
                    operand = self.fetch_byte()
                    self.__register_compare(operand, self.X)
                    break
                if case(OpCodes.INS_CPY):
                    operand = self.fetch_byte()
                    self.__register_compare(operand, self.Y)
                    break
                if case(OpCodes.INS_CPX_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.X)
                    break
                if case(OpCodes.INS_CPY_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.Y)
                    break
                if case(OpCodes.INS_CPX_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.X)
                    break
                if case(OpCodes.INS_CPY_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.Y)
                    break
                if case(OpCodes.INS_CMP):
                    operand = self.fetch_byte()
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_CMP_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_CMP_ZPX):
                    address = self.address_zero_page_x_offset()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_CMP_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_CMP_ABSX):
                    address = self.address_absolute_x_offset()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_CMP_ABSY):
                    address = self.address_absolute_y_offset()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_CMP_INDX):
                    address = self.address_indirect_x_offset()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_CMP_INDY):
                    address = self.address_indirect_y_offset()
                    operand = self.read_byte(address)
                    self.__register_compare(operand, self.A)
                    break
                if case(OpCodes.INS_ASL):
                    self.A = self.__arithmetic_shift_left(self.A)
                    break
                if case(OpCodes.INS_ASL_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    result = self.__arithmetic_shift_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ASL_ZPX):
                    address = self.address_zero_page_x_offset()
                    operand = self.read_byte(address)
                    result = self.__arithmetic_shift_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ASL_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    result = self.__arithmetic_shift_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ASL_ABSX):
                    address = self.address_absolute_x_offset()
                    operand = self.read_byte(address)
                    result = self.__arithmetic_shift_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_LSR):
                    self.A = self.__logical_shift_right(self.A)
                    break
                if case(OpCodes.INS_LSR_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    result = self.__logical_shift_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_LSR_ZPX):
                    address = self.address_zero_page_x_offset()
                    operand = self.read_byte(address)
                    result = self.__logical_shift_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_LSR_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    result = self.__logical_shift_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_LSR_ABSX):
                    address = self.address_absolute_x_offset_5()
                    operand = self.read_byte(address)
                    result = self.__logical_shift_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROL):
                    self.A = self.__rotate_left(self.A)
                    break
                if case(OpCodes.INS_ROL_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    result = self.__rotate_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROL_ZPX):
                    address = self.address_zero_page_x_offset()
                    operand = self.read_byte(address)
                    result = self.__rotate_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROL_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    result = self.__rotate_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROL_ABSX):
                    address = self.address_absolute_x_offset_5()
                    operand = self.read_byte(address)
                    result = self.__rotate_left(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROR):
                    self.A = self.__rotate_right(self.A)
                    break
                if case(OpCodes.INS_ROR_ZP):
                    address = self.address_zero_page()
                    operand = self.read_byte(address)
                    result = self.__rotate_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROR_ZPX):
                    address = self.address_zero_page_x_offset()
                    operand = self.read_byte(address)
                    result = self.__rotate_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROR_ABS):
                    address = self.address_absolute()
                    operand = self.read_byte(address)
                    result = self.__rotate_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_ROR_ABSX):
                    address = self.address_absolute_x_offset_5()
                    operand = self.read_byte(address)
                    result = self.__rotate_right(operand)
                    self.write_byte(address, result)
                    break
                if case(OpCodes.INS_BRK):
                    self.push_pc_plus_1_onto_stack()
                    self.__push_processor_status_onto_stack()
                    interrupt_vector = 0xFFFE
                    self.program_counter = self.read_word(interrupt_vector)
                    self.Flag.B = int(True)
                    self.Flag.I = int(True)
                    break
                if case(OpCodes.INS_RTI):
                    self.__pop_processor_status_from_stack()
                    self.processor_status = Byte(self.pop_word_from_stack())
                    break
                # default
                raise NotImplementedError(f"Instruction {instruction} not handled")
        num_cycles_used = num_cycles_requested - self.cycles
        return num_cycles_used
