import ctypes


class CType(int):
    def __init__(self, n: int):
        raise NotImplementedError

    def __repr__(self):
        return repr(self.n.value)

    def __add__(self, other):
        return self.__class__(self.n.value + int(other))

    # This is soon to become deprecated
    def __int__(self):
        return self.n.value

    def __eq__(self, other: object) -> bool:
        return int(self.n.value) == int(other)


class Byte(CType):
    def __init__(self, n: int):
        self.ctype = ctypes.c_ubyte
        self.n = self.ctype(n)


class Word(CType):
    def __init__(self, n: int):
        self.ctype = ctypes.c_ushort
        self.n = self.ctype(n)


class SByte(CType):
    def __init__(self, n: int):
        self.ctype = ctypes.c_char
        self.n = self.ctype(n)


class u32(CType):
    def __init__(self, n: int):
        self.ctype = ctypes.c_uint32
        self.n = self.ctype(n)


class s32(CType):
    def __init__(self, n: int):
        self.ctype = ctypes.c_int32
        self.n = self.ctype(n)
