"""
Prime number utilities.

Provides:
  - is_prime_slow   : deterministic trial-division test
  - is_prime_miller : probabilistic Miller-Rabin test
  - is_prime        : convenience alias (uses Miller-Rabin by default)
  - next_prime      : smallest prime strictly greater than n
"""

import math
import random


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_integer(n, name="n"):
    """Raise TypeError/ValueError for non-integer-like inputs."""
    if isinstance(n, float):
        if not n.is_integer():
            raise ValueError(f"{name} must be an integer, got float {n}")
        return int(n)
    if not isinstance(n, int):
        raise TypeError(f"{name} must be an integer, got {type(n).__name__}")
    return n


# ---------------------------------------------------------------------------
# Deterministic trial-division  O(√n)
# ---------------------------------------------------------------------------

def is_prime_slow(n) -> bool:
    """
    Deterministic primality test using trial division.

    Always correct but slow for large numbers (O(√n) divisions).
    Accepts whole-number floats like 7.0; raises for fractional floats.
    """
    n = _check_integer(n, "n")
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    # Check odd divisors up to √n
    for i in range(3, math.isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True


# ---------------------------------------------------------------------------
# Probabilistic Miller-Rabin test
# ---------------------------------------------------------------------------

def _miller_rabin_round(n: int, a: int) -> bool:
    """
    One witness round of Miller-Rabin.
    Returns False if `a` is a witness that `n` is composite.
    """
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    x = pow(a, d, n)  # fast modular exponentiation
    if x == 1 or x == n - 1:
        return True  # probably prime for this witness

    for _ in range(r - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False  # composite


def is_prime_miller(n, rounds: int = 20) -> bool:
    """
    Probabilistic Miller-Rabin primality test.

    For n < 3_215_031_751 the deterministic witness set {2,3,5,7} is used,
    making the result exact for those values.
    For larger n, `rounds` random witnesses are used; the false-positive
    probability is at most 4^(-rounds).

    Accepts whole-number floats; raises for fractional floats.
    """
    n = _check_integer(n, "n")
    if n < 2:
        return False
    if n in (2, 3, 5, 7):
        return True
    if n % 2 == 0:
        return False

    # Deterministic witnesses sufficient for n < 3_215_031_751
    if n < 3_215_031_751:
        witnesses = [2, 3, 5, 7]
    else:
        # Random witnesses for larger numbers
        witnesses = [random.randrange(2, n - 1) for _ in range(rounds)]

    return all(_miller_rabin_round(n, a) for a in witnesses)


# ---------------------------------------------------------------------------
# Convenience alias
# ---------------------------------------------------------------------------

def is_prime(n) -> bool:
    """Return True if n is prime. Uses Miller-Rabin (fast, probabilistic)."""
    return is_prime_miller(n)


# ---------------------------------------------------------------------------
# Next prime
# ---------------------------------------------------------------------------

def next_prime(n) -> int:
    """
    Return the smallest prime strictly greater than n.

    Accepts whole-number floats (rounds them to int first);
    raises for fractional floats and non-numeric types.
    """
    if isinstance(n, float):
        # Round fractional floats to nearest int, then find next prime above that
        n = math.floor(n)
    else:
        n = _check_integer(n, "n")

    candidate = n + 1
    # Ensure candidate is at least 2
    if candidate < 2:
        return 2
    # Step through candidates until we find a prime
    while not is_prime_miller(candidate):
        candidate += 1
    return candidate
