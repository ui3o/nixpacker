#!/bin/bash

if [ ! -d ~/.config/nip ]; then
    mkdir -p ~/.config/nip
    cp /nip/config.py ~/.config/nip/config.py
fi
cp /nip/typings.py ~/.config/nip/typings.py

mkdir -p /nix/warehouse/nip
cp /nip/config.py /nix/warehouse/nip/config.py
cp /nip/typings.py /nix/warehouse/nip/typings.py
cp /nip/nip /nix/warehouse/nip/nip

