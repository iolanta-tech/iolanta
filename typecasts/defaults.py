from functools import partial

from typecasts.main import Typecasts

DefaultTypecasts = Typecasts()


# Basic, primitive casts
DefaultTypecasts.update({
    (int, float): float,
    (int, bytes): bytes,
})

# String to bytes and vice versa
DefaultTypecasts.update({
    (bytes, str): partial(bytes.decode, encoding='utf-8'),
    (str, bytes): str.encode,
})

# Misc experiments
DefaultTypecasts.update({
    (float, int): int,
})

