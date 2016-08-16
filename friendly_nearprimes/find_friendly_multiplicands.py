# The aim of this program is to output two nubmers that can be programmed into
# user-cascaded counters in the AP chip to come fairly close to a prime target
# number. 

# a counter's max target is 2^11 or 2,048
# Any number below this can be hit by a single counter - this program is not
# needed
# for numbers between 2,048 and 4,194,304 (2^22) we want to use two multiples
# each of which is below 2,048. In many cases we can directly hit the target
# value. But in other cases we might only be able to come close. 
# We want to come as close as possible. 

import copy
import math

def prime_factors(n):
    """Returns all the prime factors of a positive integer"""
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n /= d
        d = d + 1
        if d*d > n:
            if n > 1: factors.append(n)
            break
    return factors

def works(factorlist):
    if max(factorlist) < 2048:
        return True
    return False

def find_friendly_multiplicands(target):
    if target <= 2048:
        print "Just us a single counter"
        return None

    factorlist = None
    for offset in [0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -6, 6, -7, 7, -8, 8, -9, 9, -10, 10, -11, 11, -12, 12, -13, 13]:
        new_target = target + offset
        factorlist = prime_factors(new_target)
        if works(factorlist):
            break
    orig_factorlist = copy.deepcopy(factorlist)
    #print "%d + %d solution found: %s" % (target, offset, factorlist)
    m1 = 1
    factorlist.sort()
    m1 = factorlist.pop()
    while m1 * factorlist[0] < 2048:
        m1 = m1 * factorlist.pop(0)
    # The last factor pushed us over 2048. Put it back
    m2 = 1
    for factor in factorlist:
        m2 *= factor
    if m1 > 2048 or m2 > 2048:
        print "ERROR %s   " % orig_factorlist,
    return ([m1, m2], offset)

if __name__ == "__main__":
    import sys
    for line in sys.stdin.readlines():
        val = int(line.strip())
        res, err = find_friendly_multiplicands(val)
        print "target %d => %d * %d = %d err = %d" % (val, res[0], res[1], res[0]*res[1], err) 
