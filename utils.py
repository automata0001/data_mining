import math
import operator as op

import settings


def to_base(n, b):
    """Returns n in base b representation as a list of digits."""
    digits = []
    while n > 0:
        digits.insert(0, n % b)
        n = n // b
    return digits

# From: http://stackoverflow.com/a/4941932/1193738
def ncr(n, r):
    """Calculates n choose r."""
    if n < r: return 0
    r = min(r, n - r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n - r, -1))
    denom = reduce(op.mul, xrange(1, r + 1))
    return numer // denom

# From: http://stackoverflow.com/a/22808285/1193738
def get_prime_factors(n):
    """Returns a list of the prime factors of n."""
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

def get_counter_factors(n):
    """Calculates the counter target values required to count to n.

    Args:
        n: Counter target value to factorize.

    Returns:
        A list of 1, 2, or 3 factors as follows:

        - If n <= 2^11, returns a list containing n.
        - If n is in (2^11, 2^22] and can be factored into 2 numbers p and q, 
          each of which is <= 2^11, returns a list containing p and q.
        - Otherwise, returns a list containing p, q, and r, where
            p is 2^11;
            q is the largest multiplicand of 2^11 such that 2^11 * q < n;
            r is the difference of n - p*q.
    """
    if n <= settings.MAX_SINGLE_TARGET:
        return [n]
    elif n > settings.MAX_DOUBLE_TARGET:
        raise NotImplementedError('target must be <= {}'.format(settings.MAX_DOUBLE_TARGET))

    factors = get_prime_factors(n)
    pair = balanced_factor_pair(factors, 1, 1, 0)
    if max(pair) > settings.MAX_SINGLE_TARGET:
        q = n // settings.MAX_SINGLE_TARGET
        r = n - (settings.MAX_SINGLE_TARGET * q)
        return [settings.MAX_SINGLE_TARGET, q, r]
    else:
        return pair

def balanced_factor_pair(factors, x, y, i):
    """Finds the most balanced pair of factors from the given prime factor list.

    Here, balanced means both factors are minimized such that the sum of the two
    factors is less than the sum of all other possible factor pairs.

    Call with x and y initially set to 1, and i initially set to 0.

    Args:
        factors: List of prime factors.
        x: Result factor x.
        y: Result factor y.
        i: Current index into factors list.

    Returns:
        A minimized factor pair as a list, [x, y].
    """
    if len(factors[i:]) == 0:
        return [x, y]
    elif i == 0:
        return balanced_factor_pair(factors, x * factors[i], y, i + 1)
    else:
        x1, y1 = balanced_factor_pair(factors, x * factors[i], y, i + 1)
        x2, y2 = balanced_factor_pair(factors, x, y * factors[i], i + 1)

        if x1 + y1 <= x2 + y2:
            return [x1, y1]
        else:
            return [x2, y2]

def normalize_minsup(minsup, lines):
    """Returns minsup as an absolute number of lines.
    
    Args:
        minsup: String representing minimum support value. Can be an integer (n)
                or a percentage (n%). 
        lines: Number of lines (transactions) in the dataset.

    Returns:
        An integer representing the minimum support as an absolute number of lines.
    """
    if minsup[-1] == '%':
        return int((float(minsup[:-1]) / 100) * lines)
    else:
        return int(minsup)


# vim: nu:et:ts=4:sw=4:fdm=indent
