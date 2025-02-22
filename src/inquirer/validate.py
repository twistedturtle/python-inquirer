

import hashlib



def is_integer(answers, current):
    if current.isdecimal():
        return True
    return False

def is_decimal(answers, current):
    if current.isdecimal():
        return True
    return False

def is_digit(answers, current):
    if current.isdigit():
        return True
    return False


def is_alpha(answers, current):
    if current.isalpha():
        return True
    return False

def is_alphanumeric(answers, current):
    if current.isalnum():
        return True
    return False


def is_hashlib(answers, current):
    if current in hashlib.algorithms_guaranteed:
        return True
    return False

