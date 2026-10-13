"""Educational RSA-group Wesolowski VDF using sequential modular squaring.

Not a production cryptographic protocol: the challenge is 64-bit and the group
modulus supplied by callers has not been generated as an unknown-order group.
"""
import hashlib
import math
from typing import Dict

MAX_ITERATIONS = 10000
MAX_MODULUS_BITS = 4096
_MR_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def _validate(modulus: int, base: int, iterations: int) -> None:
    if any(type(v) is not int for v in (modulus, base, iterations)):
        raise ValueError("modulus, base, and iterations must be integers")
    if not (9 <= modulus and modulus % 2 == 1 and modulus.bit_length() <= MAX_MODULUS_BITS):
        raise ValueError("modulus must be odd, at least 9, and at most 4096 bits")
    if not (2 <= base <= modulus - 2) or math.gcd(base, modulus) != 1:
        raise ValueError("base must be between 2 and modulus-2 and coprime to modulus")
    if not 1 <= iterations <= MAX_ITERATIONS:
        raise ValueError(f"iterations must be between 1 and {MAX_ITERATIONS}")


def _prime64(value: int) -> bool:
    if value < 2:
        return False
    for small in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % small == 0:
            return value == small
    d, s = value - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _MR_BASES:
        if a % value == 0:
            continue
        z = pow(a, d, value)
        if z == 1 or z == value - 1:
            continue
        for _ in range(s - 1):
            z = z * z % value
            if z == value - 1:
                break
        else:
            return False
    return True


def challenge_prime(modulus: int, base: int, iterations: int, output: int) -> int:
    """Derive a 64-bit prime from the complete evaluation transcript."""
    transcript = f"wesolowski-demo-v1|{modulus}|{base}|{iterations}|{output}"
    digest = hashlib.sha256(transcript.encode("ascii")).digest()
    candidate = int.from_bytes(digest[:8], "big") | (1 << 63) | 1
    while not _prime64(candidate):
        candidate += 2
        if candidate >= 1 << 64:
            candidate = (1 << 63) + 1
    return candidate


def evaluate(modulus: int, base: int, iterations: int) -> int:
    """Compute base**(2**iterations) mod modulus using sequential squarings."""
    _validate(modulus, base, iterations)
    output = base
    for _ in range(iterations):
        output = output * output % modulus
    return output


def prove(modulus: int, base: int, iterations: int) -> Dict[str, int]:
    """Generate Wesolowski's quotient proof using O(iterations) space-free division."""
    output = evaluate(modulus, base, iterations)
    challenge = challenge_prime(modulus, base, iterations, output)
    proof, remainder = 1, 1
    # Long-divide the exponent 2**iterations by challenge, processing
    # the leading binary 1 followed by `iterations` zero bits.
    for _ in range(iterations):
        doubled = remainder * 2
        bit = int(doubled >= challenge)
        remainder = doubled % challenge
        proof = proof * proof % modulus
        if bit:
            proof = proof * base % modulus
    return {
        "modulus": modulus,
        "base": base,
        "iterations": iterations,
        "output": output,
        "proof": proof,
        "challenge": challenge,
        "remainder": remainder,
    }


def verify(result: Dict[str, int]) -> bool:
    """Verify a transcript-bound proof without repeating sequential squaring."""
    try:
        modulus, base, iterations = (result[k] for k in ("modulus", "base", "iterations"))
        _validate(modulus, base, iterations)
        output, proof, challenge, remainder = (
            result[k] for k in ("output", "proof", "challenge", "remainder")
        )
        if any(type(v) is not int for v in (output, proof, challenge, remainder)):
            return False
        if not (0 <= output < modulus and 1 <= proof < modulus):
            return False
        if challenge != challenge_prime(modulus, base, iterations, output):
            return False
        if remainder != pow(2, iterations, challenge):
            return False
        return (pow(proof, challenge, modulus) * pow(base, remainder, modulus)) % modulus == output
    except (KeyError, TypeError, ValueError):
        return False
