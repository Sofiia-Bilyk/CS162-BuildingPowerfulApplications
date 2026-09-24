"""
Unit tests for primes.py
Run with:  pytest test_primes.py -v
Coverage:  pytest test_primes.py --cov=primes --cov-report=term-missing
"""

import pytest
from primes import is_prime_slow, is_prime_miller, is_prime, next_prime


# ---------------------------------------------------------------------------
# Known primes / composites used across several tests
# ---------------------------------------------------------------------------
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
SMALL_COMPOSITES = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 25, 49]


# ===========================================================================
# is_prime_slow (deterministic)
# ===========================================================================

class TestIsPrimeSlow:

    # --- basic correctness ---

    def test_known_primes(self):
        for p in SMALL_PRIMES:
            assert is_prime_slow(p), f"{p} should be prime"

    def test_known_composites(self):
        for c in SMALL_COMPOSITES:
            assert not is_prime_slow(c), f"{c} should not be prime"

    def test_one_is_not_prime(self):
        assert not is_prime_slow(1)

    def test_zero_is_not_prime(self):
        assert not is_prime_slow(0)

    def test_negative_numbers_are_not_prime(self):
        for n in [-1, -2, -7, -100]:
            assert not is_prime_slow(n)

    def test_large_prime(self):
        # 7919 is the 1000th prime
        assert is_prime_slow(7919)

    def test_large_composite(self):
        assert not is_prime_slow(7921)  # 89^2

    # --- whole-number floats accepted ---

    def test_whole_float_prime(self):
        assert is_prime_slow(7.0)

    def test_whole_float_composite(self):
        assert not is_prime_slow(9.0)

    # --- bad inputs ---

    def test_fractional_float_raises(self):
        with pytest.raises(ValueError):
            is_prime_slow(3.5)

    def test_string_raises(self):
        with pytest.raises(TypeError):
            is_prime_slow("7")

    def test_none_raises(self):
        with pytest.raises(TypeError):
            is_prime_slow(None)

    def test_list_raises(self):
        with pytest.raises(TypeError):
            is_prime_slow([7])


# ===========================================================================
# is_prime_miller (probabilistic)
# ===========================================================================

class TestIsPrimeMiller:

    def test_known_primes(self):
        for p in SMALL_PRIMES:
            assert is_prime_miller(p), f"{p} should be prime"

    def test_known_composites(self):
        for c in SMALL_COMPOSITES:
            assert not is_prime_miller(c), f"{c} should not be prime"

    def test_one_is_not_prime(self):
        assert not is_prime_miller(1)

    def test_zero_is_not_prime(self):
        assert not is_prime_miller(0)

    def test_negative_numbers_are_not_prime(self):
        for n in [-1, -2, -13]:
            assert not is_prime_miller(n)

    def test_large_prime_below_threshold(self):
        # Deterministic branch (n < 3_215_031_751)
        assert is_prime_miller(7919)

    def test_large_prime_above_threshold(self):
        # Probabilistic branch — 10^15 + 37 is prime
        assert is_prime_miller(1_000_000_000_000_037)

    def test_large_composite_above_threshold(self):
        assert not is_prime_miller(1_000_000_000_000_000)  # divisible by 2

    def test_whole_float_prime(self):
        assert is_prime_miller(11.0)

    def test_fractional_float_raises(self):
        with pytest.raises(ValueError):
            is_prime_miller(2.5)

    def test_string_raises(self):
        with pytest.raises(TypeError):
            is_prime_miller("prime")

    def test_none_raises(self):
        with pytest.raises(TypeError):
            is_prime_miller(None)


# ===========================================================================
# is_prime (alias — just confirm it delegates correctly)
# ===========================================================================

class TestIsPrimeAlias:

    def test_prime(self):
        assert is_prime(17)

    def test_composite(self):
        assert not is_prime(18)

    def test_agrees_with_slow_for_small_numbers(self):
        for n in range(-10, 200):
            assert is_prime_slow(n) == is_prime(n), f"Mismatch at {n}"


# ===========================================================================
# next_prime
# ===========================================================================

class TestNextPrime:

    def test_next_prime_from_zero(self):
        assert next_prime(0) == 2

    def test_next_prime_from_one(self):
        assert next_prime(1) == 2

    def test_next_prime_from_prime(self):
        # Next prime after a prime skips to the one after it
        assert next_prime(2) == 3
        assert next_prime(3) == 5
        assert next_prime(7) == 11
        assert next_prime(13) == 17

    def test_next_prime_from_composite(self):
        assert next_prime(4) == 5
        assert next_prime(8) == 11
        assert next_prime(14) == 17

    def test_next_prime_from_negative(self):
        assert next_prime(-10) == 2
        assert next_prime(-1) == 2

    def test_next_prime_large(self):
        # Prime after 7919 (1000th prime) is 7927
        assert next_prime(7919) == 7927

    # --- float inputs ---

    def test_whole_float_rounds(self):
        # 7.0 → treat as 7 → next prime is 11
        assert next_prime(7.0) == 11

    def test_fractional_float_floors(self):
        # 7.9 floors to 7 → next prime is 11
        assert next_prime(7.9) == 11

    def test_fractional_float_low(self):
        # 1.1 floors to 1 → next prime is 2
        assert next_prime(1.1) == 2

    def test_fractional_float_just_below_prime(self):
        # 4.9 floors to 4 → next prime is 5
        assert next_prime(4.9) == 5

    # --- bad inputs ---

    def test_string_raises(self):
        with pytest.raises(TypeError):
            next_prime("five")

    def test_none_raises(self):
        with pytest.raises(TypeError):
            next_prime(None)

    def test_list_raises(self):
        with pytest.raises(TypeError):
            next_prime([5])
