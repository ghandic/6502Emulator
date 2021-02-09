from truth.truth import AssertThat

from ..emulator.utils import switch


def test_cpu_repr(cpu):
    cpu.A = 1
    cpu.Y = 5
    cpu.X = 3
    AssertThat(cpu.__repr__()).IsEqualTo("A: 1 X: 3 Y: 5\nPC: 65532 SP: 255\nPS: 255\n")


def test_cpu_stack_pointer_to_address(cpu):
    AssertThat(cpu.sp_to_address).IsEqualTo(511)


def test_switch_match():
    for case in switch("A"):
        AssertThat(case("A")).IsTruthy()
        AssertThat(case("B")).IsFalsy()
        AssertThat(case(ord("A"))).IsFalsy()


def test_switch_match_break():
    for case in switch("A"):
        if case("A"):
            break
    else:
        assert False


def test_switch_match_nobreak():
    for case in switch("A"):
        if case("B"):
            break
    else:  # default
        assert True
