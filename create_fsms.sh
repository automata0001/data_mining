#!/bin/bash

[[ $# -lt 1 ]] && { echo "usage: $(basename $0) MAX_K" >&2; exit; }

python create_fsms.py -k $1

for fsm in fsm/i[0-9]c[0-9]k[0-9].fsm; do
    apadmin --output=${fsm%.fsm}x8.fsm --union $fsm $fsm $fsm $fsm $fsm $fsm $fsm $fsm
done
