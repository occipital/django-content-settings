import pytest
import operator
import sys

from content_settings.types.lazy import LazyObject


@pytest.fixture
def lazy_int():
    return LazyObject(lambda: 5)


@pytest.fixture
def lazy_list():
    return LazyObject(lambda: [1, 2, 3])


@pytest.fixture
def lazy_string():
    return LazyObject(lambda: "hello")


@pytest.fixture
def lazy_obj():
    class Dummy:
        def mult5(self, val):
            return val * 5

    return LazyObject(lambda: Dummy())


@pytest.fixture
def lazy_function():
    return LazyObject(lambda: lambda x: x + 5)


def test_getattr(lazy_obj):
    assert lazy_obj.mult5(2) == 10


def test_bytes(lazy_int):
    assert bytes(lazy_int) == bytes(5)


def test_str(lazy_int):
    assert str(lazy_int) == "5"


def test_bool(lazy_int):
    assert bool(lazy_int)


def test_dir(lazy_int):
    assert "real" in dir(lazy_int)


def test_hash(lazy_int):
    assert hash(lazy_int) == hash(5)


def test_class(lazy_int):
    assert lazy_int.__class__ == int


def test_eq(lazy_int):
    assert lazy_int == 5


def test_lt(lazy_int):
    assert lazy_int < 10


def test_le(lazy_int):
    assert lazy_int <= 5


def test_gt(lazy_int):
    assert lazy_int > 4


def test_ge(lazy_int):
    assert lazy_int >= 5


def test_ne(lazy_int):
    assert lazy_int != 6


def test_mod(lazy_int):
    assert lazy_int % 2 == 1


def test_getitem(lazy_list):
    assert lazy_list[0] == 1


def test_iter(lazy_list):
    assert list(iter(lazy_list)) == [1, 2, 3]


def test_len(lazy_list):
    assert len(lazy_list) == 3


def test_contains(lazy_list):
    assert 2 in lazy_list


def test_mul(lazy_int):
    assert lazy_int * 2 == 10


def test_rmul(lazy_int):
    assert 2 * lazy_int == 10


def test_abs(lazy_int):
    assert abs(lazy_int) == 5


def test_add(lazy_int):
    assert lazy_int + 3 == 8


def test_radd(lazy_int):
    assert 3 + lazy_int == 8


def test_and(lazy_int):
    assert (lazy_int & 1) == (5 & 1)


def test_floordiv(lazy_int):
    assert lazy_int // 2 == 2


def test_index(lazy_int):
    assert operator.index(lazy_int) == 5


def test_inv(lazy_int):
    assert ~lazy_int == ~5


def test_invert(lazy_int):
    assert operator.invert(lazy_int) == ~5


def test_matmul(lazy_list):
    with pytest.raises(TypeError):
        lazy_list @ lazy_list


def test_neg(lazy_int):
    assert -lazy_int == -5


def test_or(lazy_int):
    assert lazy_int | 1 == 5 | 1


def test_pos(lazy_int):
    assert +lazy_int == +5


def test_pow(lazy_int):
    assert lazy_int**2 == 25


def test_sub(lazy_int):
    assert lazy_int - 2 == 3


def test_truediv(lazy_int):
    assert lazy_int / 2 == 2.5


def test_xor(lazy_int):
    assert lazy_int ^ 1 == 5 ^ 1


def test_concat(lazy_string):
    assert lazy_string + " world" == "hello world"


def test_next():
    lazy_iter = LazyObject(lambda: iter([1, 2, 3]))
    assert next(lazy_iter) == 1


def test_reversed(lazy_list):
    assert list(reversed(lazy_list)) == [3, 2, 1]


def test_round(lazy_int):
    assert round(lazy_int) == 5


def test_call(lazy_function):
    assert lazy_function(5) == 10


def test_iadd(lazy_int):
    lazy_int += 3
    assert lazy_int == 8


def test_iand(lazy_int):
    lazy_int &= 1
    assert lazy_int == 1


def test_iconcat(lazy_string):
    lazy_string += " world"
    assert lazy_string == "hello world"


def test_ifloordiv(lazy_int):
    lazy_int //= 2
    assert lazy_int == 2


def test_ilshift():
    lazy_int = LazyObject(lambda: 1)
    lazy_int <<= 2
    assert lazy_int == 4


def test_imod(lazy_int):
    lazy_int %= 2
    assert lazy_int == 1


def test_imul(lazy_int):
    lazy_int *= 2
    assert lazy_int == 10


def test_imatmul():
    with pytest.raises(TypeError):
        lazy_list = LazyObject(lambda: [1, 2, 3])
        lazy_list @= lazy_list


def test_ior(lazy_int):
    lazy_int |= 1
    assert lazy_int == 5 | 1


def test_ipow(lazy_int):
    lazy_int **= 2
    assert lazy_int == 25


def test_isub(lazy_int):
    lazy_int -= 2
    assert lazy_int == 3


def test_itruediv(lazy_int):
    lazy_int /= 2
    assert lazy_int == 2.5


def test_ixor(lazy_int):
    lazy_int ^= 1
    assert lazy_int == 4
