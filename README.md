# 6502Emulator using Python

Learning how a CPU works by emulating one - this is a port of a [6502Emulator written in C++ by davepoo](https://github.com/davepoo/6502Emulator)

This original C++ code was written during the youtube video : https://youtu.be/qJgsuQoy9bc

## Notes from original repo

### Notes 11/2020 NOTES / TODO

* All 6502 legal opcodes emulated
* Decimal mode is not handled
* Test program [/Klaus2m5/6502_65C02_functional_tests](https://github.com/Klaus2m5/6502_65C02_functional_tests) - will succeed if decimal is disabled.
* Counting cycles individually for each part of an instruction is cumbersome and probably should just deduct the correct number at the end of the instruction.
* There is no way to issue and interrupt to this virtual CPU
* There are no hooks for debugging.
* There is is no dissasembler or UI, this is just the CPU emulator & units test.
* There are no asserts if you write memory outside of the bounds (it will overwrite memory)
* Illegal opcodes are not implemented, the program will throw an exception.

### Issues

* Does the BRK command break when interrupts are disabled? that needs testing.
* PLP clears the break flag when executed? is this correct?
* INS_JMP_ABS, see notes about bug in 6502 for correct emulation 

### What did we learn from this?

* A program is just big array bytes
* Writing a CPU emulator is time consuming
* Some features are undocumented!
* Emulating a CPU is harder you than you think, because you have emulate things you got for free in a real CPU (like the clock)
* Writing Unit tests for the CPU was a good idea.
* Big switch state works for small instruction set processors, probably not for bigger ones, like the 68000.
