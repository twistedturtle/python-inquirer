import pytest

from inquirer.errors import ValidationError
from inquirer import validate as v

decimal_values = ["0", "1", "2", "3"]
not_decimal_values = ["0.3", "a", "⅛", "@", "1e10"]

digit_values = decimal_values
not_digit_values = ["0.3", "a", "½", "@", "1e10"]

float_values = ["0.1", "1", "1e10", "0.1e10", ".1"]
not_float_values = ["a", "@", "helo1"]

alpha_values = ["hello"]
not_alpha_values = ["hell3", "@", "54"]

alphanumeric_values = ["hell3"]
not_alphanumeric_values = ["@", "/"]

path_values = []
not_path_values = []


def test_is_decimal():
    for value in decimal_values:
        assert v.is_decimal([], value) is True


def test_is_decimal_invalid():
    for value in not_decimal_values:
        with pytest.raises(ValidationError):
            v.is_decimal([], value)


def test_is_digit():
    for value in decimal_values:
        assert v.is_digit([], value) is True


def test_is_digit_invalid():
    for value in not_decimal_values:
        with pytest.raises(ValidationError):
            v.is_digit([], value)


def test_is_alpha():
    for value in alpha_values:
        assert v.is_alpha([], value) is True


def test_alpha_invalid():
    for value in not_alpha_values:
        with pytest.raises(ValidationError):
            v.is_alpha([], value)


def test_is_alphanumeric():
    for value in alphanumeric_values:
        assert v.is_alphanumeric([], value) is True


def test_is_alphanumeric_invalid():
    for value in not_alphanumeric_values:
        with pytest.raises(ValidationError):
            v.is_alphanumeric([], value)


def test_is_hashlib():
    assert v.is_hashlib([], "sha1") is True


def test_is_hashlib_invalid():
    with pytest.raises(ValidationError):
        v.is_hashlib([], "gerbil")


def test_is_float():
    for value in float_values:
        assert v.is_float([], value) is True


def test_is_float_invalid():
    for value in not_float_values:
        with pytest.raises(ValidationError):
            v.is_float([], value)


# def test_is_path():
#   assert v.is_path()

# def test_is_path_invalid():
#   pass

# def test_is_portable_path():
#   pass

# def test_is_date():
#   pass

# def test_is_datetime():
#   pass

# def test_is_time():
#   pass
