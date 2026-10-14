"""SIMON 128/128 reference model (Beaulieu et al., "The SIMON and SPECK
Families of Lightweight Block Ciphers", 2013). Used as the golden model for
the cocotb tests. Checked against the paper's test vector in test.py."""

MASK = (1 << 64) - 1
ROUNDS = 68
Z2 = "10101111011100000011010010011000101000010001111110010110110011"


def _rol(x, r):
    return ((x << r) | (x >> (64 - r))) & MASK


def _ror(x, r):
    return ((x >> r) | (x << (64 - r))) & MASK


def round_keys(key):
    k = [key & MASK, key >> 64]
    for i in range(2, ROUNDS):
        t = _ror(k[i - 1], 3)
        t ^= _ror(t, 1)
        k.append((~k[i - 2] ^ t ^ int(Z2[(i - 2) % 62]) ^ 3) & MASK)
    return k


def encrypt(plaintext, key):
    """plaintext and key are 128-bit integers; returns the 128-bit ciphertext."""
    x, y = plaintext >> 64, plaintext & MASK
    for rk in round_keys(key):
        x, y = y ^ (_rol(x, 1) & _rol(x, 8)) ^ _rol(x, 2) ^ rk, x
    return (x << 64) | y
