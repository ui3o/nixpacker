#!/bin/bash

python3 /template/process.py $@
status=$?

[ $status -eq 78 ] && chmod ugo+x /script && /script

