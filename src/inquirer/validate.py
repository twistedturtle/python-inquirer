import hashlib

from inquirer.errors import ValidationError


def is_decimal(answers, current):
    if current.isdecimal():
        return True
    raise ValidationError("", reason=f'"{current}" is not a base 10 integer')


def is_digit(answers, current):
    if current.isdigit():
        return True
    raise ValidationError("", reason=f'"{current}" is not a number')


def is_float(answers, current):
    try:
        float(current)
        return True
    except ValueError:
        raise ValidationError("", reason=f'"{current}" is not a float')


def is_alpha(answers, current):
    if current.isalpha():
        return True
    raise ValidationError("", reason=f'"{current}" is not a alphabetical')


def is_alphanumeric(answers, current):
    if current.isalnum():
        return True
    raise ValidationError("", reason=f'"{current}" is not alphanumeric')


def is_hashlib(answers, current):
    if current in hashlib.algorithms_guaranteed:
        return True
    raise ValidationError("", reason=f'"{current}" is not a hash in hashlib')
