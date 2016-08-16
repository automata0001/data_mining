
import find_friendly_multiplicands as ffm

FH = open ("primes_from_2053_to_4194301.txt")
for line in FH.readlines():
    target = int(line)
    res, err = ffm.find_friendly_multiplicands(target)
    print "target %d => %d * %d = %d %d" % (target, res[0], res[1], res[0]*res[1], err) 

