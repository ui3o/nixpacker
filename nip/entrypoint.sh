#!/bin/bash

ln -sf ~/.config/nip /nip_cfg
ln -sf ~/.nix/warehouse /nix/warehouse
python3 /template/process.py $@
status=$?

[ $status -eq 78 ] && python3 /template/port.watcher.py > /var/log/port.watcher.log &
[ $status -eq 78 ] && source /nix/store/paths && chmod ugo+x /script && /script

