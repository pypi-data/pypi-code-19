def modular_multiplicative_inverse(number: int,
                                   modulus: int) -> int:
    if number == 0:
        return 0
    x_1, x_2 = 1, 0
    u, v = number, modulus
    while u > 1:
        q = v // u
        x_1, x_2 = x_2 - q * x_1, x_1
        remainder = v - q * u
        u, v = remainder, u
    return x_1 % modulus
