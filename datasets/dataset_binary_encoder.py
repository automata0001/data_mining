# Reads in a dataset where IDs are presented as base-10 strings
# converts the base-10 items to 8-bit binary encoding 
# also injects transaction delimeters (0xFF bytes)

import sys

BYTE_1, BYTE_2 = range(2) # an 'enum' for bytes per item
MAX_BYTE_2_ITEMID = 65024
MOD_VAL = 255
DELIMETER = 255
DEBUG = False

encoding = BYTE_1
OFH = open("out.bin","wb")

def byte_2_encode(integer_list):
    new_list = []
    for i in integer_list:
        if i > MAX_BYTE_2_ITEMID:
            print "ERROR: 2-byte encoding restricted to values under %s" \
                    % (MAX_BYTE_2_ITEMID - 1)
            sys.exit()
        if i < MOD_VAL:
            new_list.append(0)
            new_list.append(i)
        else:
            #i += 1
            high_byte = i / MOD_VAL
            low_byte = i % MOD_VAL
            if DEBUG: print "%d => %02x %02x" % (i, high_byte, low_byte)
            new_list.append(high_byte)
            new_list.append(low_byte)
    return new_list

# For now, read input from STDIN
for line in sys.stdin.readlines():
    items = map(int, line.split()) # convert line into array of integers
    if encoding == BYTE_2:
        items = byte_2_encode(items) # 2-byte encode, if needed
    items.insert(0, DELIMETER) # insert leading delimeter for this transaction
    items.append(DELIMETER) # insert trailing delimeter for this transaction
    output = bytearray(items) # convert the integer array to bytes
    OFH.write(output) # write to the output file

output = bytearray([DELIMETER,DELIMETER]) # add end-of-all-transactions delimeter
OFH.write(output)
OFH.close()

