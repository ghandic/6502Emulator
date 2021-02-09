from dataclasses import dataclass

from .c_types import Byte


@dataclass
class StatusFlags(object):
    C: Byte = Byte(1)  # 0: Carry Flag
    Z: Byte = Byte(1)  # 1: Zero Flag
    I: Byte = Byte(1)  # 2: Interrupt disable
    D: Byte = Byte(1)  # 3: Decimal mode
    B: Byte = Byte(1)  # 4: Break
    U: Byte = Byte(1)  # 5: Unused
    V: Byte = Byte(1)  # 6: Overflow
    N: Byte = Byte(1)  # 7: Negative


class ProcessorStatus(object):
    NegativeFlagBit: bin = 0b10000000
    OverflowFlagBit: bin = 0b01000000
    BreakFlagBit: bin = 0b000010000
    UnusedFlagBit: bin = 0b000100000
    InterruptDisableFlagBit: bin = 0b000000100
    ZeroBit: bin = 0b00000001


class OpCodes(object):
    # LDA
    INS_LDA_IM = Byte(0xA9)
    INS_LDA_ZP = Byte(0xA5)
    INS_LDA_ZPX = Byte(0xB5)
    INS_LDA_ABS = Byte(0xAD)
    INS_LDA_ABSX = Byte(0xBD)
    INS_LDA_ABSY = Byte(0xB9)
    INS_LDA_INDX = Byte(0xA1)
    INS_LDA_INDY = Byte(0xB1)
    # LDX
    INS_LDX_IM = Byte(0xA2)
    INS_LDX_ZP = Byte(0xA6)
    INS_LDX_ZPY = Byte(0xB6)
    INS_LDX_ABS = Byte(0xAE)
    INS_LDX_ABSY = Byte(0xBE)
    # LDY
    INS_LDY_IM = Byte(0xA0)
    INS_LDY_ZP = Byte(0xA4)
    INS_LDY_ZPX = Byte(0xB4)
    INS_LDY_ABS = Byte(0xAC)
    INS_LDY_ABSX = Byte(0xBC)
    # STA
    INS_STA_ZP = Byte(0x85)
    INS_STA_ZPX = Byte(0x95)
    INS_STA_ABS = Byte(0x8D)
    INS_STA_ABSX = Byte(0x9D)
    INS_STA_ABSY = Byte(0x99)
    INS_STA_INDX = Byte(0x81)
    INS_STA_INDY = Byte(0x91)
    # STX
    INS_STX_ZP = Byte(0x86)
    INS_STX_ZPY = Byte(0x96)
    INS_STX_ABS = Byte(0x8E)
    # STY
    INS_STY_ZP = Byte(0x84)
    INS_STY_ZPX = Byte(0x94)
    INS_STY_ABS = Byte(0x8C)

    INS_TSX = Byte(0xBA)
    INS_TXS = Byte(0x9A)
    INS_PHA = Byte(0x48)
    INS_PLA = Byte(0x68)
    INS_PHP = Byte(0x08)
    INS_PLP = Byte(0x28)

    INS_JMP_ABS = Byte(0x4C)
    INS_JMP_IND = Byte(0x6C)
    INS_JSR = Byte(0x20)
    INS_RTS = Byte(0x60)

    # Logical Ops

    # AND
    INS_AND_IM = Byte(0x29)
    INS_AND_ZP = Byte(0x25)
    INS_AND_ZPX = Byte(0x35)
    INS_AND_ABS = Byte(0x2D)
    INS_AND_ABSX = Byte(0x3D)
    INS_AND_ABSY = Byte(0x39)
    INS_AND_INDX = Byte(0x21)
    INS_AND_INDY = Byte(0x31)

    # OR
    INS_ORA_IM = Byte(0x09)
    INS_ORA_ZP = Byte(0x05)
    INS_ORA_ZPX = Byte(0x15)
    INS_ORA_ABS = Byte(0x0D)
    INS_ORA_ABSX = Byte(0x1D)
    INS_ORA_ABSY = Byte(0x19)
    INS_ORA_INDX = Byte(0x01)
    INS_ORA_INDY = Byte(0x11)

    # EOR
    INS_EOR_IM = Byte(0x49)
    INS_EOR_ZP = Byte(0x45)
    INS_EOR_ZPX = Byte(0x55)
    INS_EOR_ABS = Byte(0x4D)
    INS_EOR_ABSX = Byte(0x5D)
    INS_EOR_ABSY = Byte(0x59)
    INS_EOR_INDX = Byte(0x41)
    INS_EOR_INDY = Byte(0x51)

    # BIT
    INS_BIT_ZP = Byte(0x24)
    INS_BIT_ABS = Byte(0x2C)

    # Transfer Registers
    INS_TAX = Byte(0xAA)
    INS_TAY = Byte(0xA8)
    INS_TXA = Byte(0x8A)
    INS_TYA = Byte(0x98)

    # Increments, Decrements
    INS_INX = Byte(0xE8)
    INS_INY = Byte(0xC8)
    INS_DEY = Byte(0x88)
    INS_DEX = Byte(0xCA)
    INS_DEC_ZP = Byte(0xC6)
    INS_DEC_ZPX = Byte(0xD6)
    INS_DEC_ABS = Byte(0xCE)
    INS_DEC_ABSX = Byte(0xDE)
    INS_INC_ZP = Byte(0xE6)
    INS_INC_ZPX = Byte(0xF6)
    INS_INC_ABS = Byte(0xEE)
    INS_INC_ABSX = Byte(0xFE)

    # branches
    INS_BEQ = Byte(0xF0)
    INS_BNE = Byte(0xD0)
    INS_BCS = Byte(0xB0)
    INS_BCC = Byte(0x90)
    INS_BMI = Byte(0x30)
    INS_BPL = Byte(0x10)
    INS_BVC = Byte(0x50)
    INS_BVS = Byte(0x70)

    # status flag changes
    INS_CLC = Byte(0x18)
    INS_SEC = Byte(0x38)
    INS_CLD = Byte(0xD8)
    INS_SED = Byte(0xF8)
    INS_CLI = Byte(0x58)
    INS_SEI = Byte(0x78)
    INS_CLV = Byte(0xB8)

    # Arithmetic
    INS_ADC = Byte(0x69)
    INS_ADC_ZP = Byte(0x65)
    INS_ADC_ZPX = Byte(0x75)
    INS_ADC_ABS = Byte(0x6D)
    INS_ADC_ABSX = Byte(0x7D)
    INS_ADC_ABSY = Byte(0x79)
    INS_ADC_INDX = Byte(0x61)
    INS_ADC_INDY = Byte(0x71)

    INS_SBC = Byte(0xE9)
    INS_SBC_ABS = Byte(0xED)
    INS_SBC_ZP = Byte(0xE5)
    INS_SBC_ZPX = Byte(0xF5)
    INS_SBC_ABSX = Byte(0xFD)
    INS_SBC_ABSY = Byte(0xF9)
    INS_SBC_INDX = Byte(0xE1)
    INS_SBC_INDY = Byte(0xF1)

    #  Register Comparison
    INS_CMP = Byte(0xC9)
    INS_CMP_ZP = Byte(0xC5)
    INS_CMP_ZPX = Byte(0xD5)
    INS_CMP_ABS = Byte(0xCD)
    INS_CMP_ABSX = Byte(0xDD)
    INS_CMP_ABSY = Byte(0xD9)
    INS_CMP_INDX = Byte(0xC1)
    INS_CMP_INDY = Byte(0xD1)

    INS_CPX = Byte(0xE0)
    INS_CPY = Byte(0xC0)
    INS_CPX_ZP = Byte(0xE4)
    INS_CPY_ZP = Byte(0xC4)
    INS_CPX_ABS = Byte(0xEC)
    INS_CPY_ABS = Byte(0xCC)

    #  shifts
    INS_ASL = Byte(0x0A)
    INS_ASL_ZP = Byte(0x06)
    INS_ASL_ZPX = Byte(0x16)
    INS_ASL_ABS = Byte(0x0E)
    INS_ASL_ABSX = Byte(0x1E)

    INS_LSR = Byte(0x4A)
    INS_LSR_ZP = Byte(0x46)
    INS_LSR_ZPX = Byte(0x56)
    INS_LSR_ABS = Byte(0x4E)
    INS_LSR_ABSX = Byte(0x5E)

    INS_ROL = Byte(0x2A)
    INS_ROL_ZP = Byte(0x26)
    INS_ROL_ZPX = Byte(0x36)
    INS_ROL_ABS = Byte(0x2E)
    INS_ROL_ABSX = Byte(0x3E)

    INS_ROR = Byte(0x6A)
    INS_ROR_ZP = Byte(0x66)
    INS_ROR_ZPX = Byte(0x76)
    INS_ROR_ABS = Byte(0x6E)
    INS_ROR_ABSX = Byte(0x7E)

    # misc
    INS_NOP = Byte(0xEA)
    INS_BRK = Byte(0x00)
    INS_RTI = Byte(0x40)
