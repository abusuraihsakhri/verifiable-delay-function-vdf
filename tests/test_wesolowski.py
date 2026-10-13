"""Independent arithmetic and adversarial checks for the educational VDF."""
import pytest

from vdf_engine.wesolowski import evaluate, prove, verify


@pytest.mark.parametrize(
    "modulus,base,iterations",
    [(77, 2, 1), (77, 2, 12), (1000036000099, 5, 20), (1000036000099, 5, 512)],
)
def test_proof_matches_direct_exponent(modulus, base, iterations):
    result = prove(modulus, base, iterations)
    assert evaluate(modulus, base, iterations) == pow(base, 2**iterations, modulus)
    assert result["proof"] == pow(base, (2**iterations) // result["challenge"], modulus)
    assert verify(result)


@pytest.mark.parametrize("key", ("output", "proof", "challenge", "remainder", "base", "iterations", "modulus"))
def test_modified_transcript_fails(key):
    result = prove(1000036000099, 5, 80)
    result[key] += 1
    assert not verify(result)


@pytest.mark.parametrize("args", [(8, 5, 10), (77, 7, 10), (77, 2, 0), (77, 2, 10001), (10, 3, 2), (77, 2.0, 2)])
def test_invalid_inputs(args):
    with pytest.raises(ValueError):
        prove(*args)


def test_prime_challenge_is_64bit_and_deterministic():
    result = prove(77, 2, 100)
    assert 2**63 <= result["challenge"] < 2**64
    assert result == prove(77, 2, 100)


def test_missing_proof_rejected():
    result = prove(77, 2, 2)
    del result["proof"]
    assert not verify(result)
