#!/bin/bash

python3 /template/process.py $@
status=$?

[ $status -eq 78 ] && source /nix/store/paths && chmod ugo+x /script && /script

