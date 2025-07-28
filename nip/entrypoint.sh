#!/bin/bash

if [ ! -d ~/.config/nip ]; then
    mkdir -p ~/.config/nip
    cp /nip/config.py ~/.config/nip/config.py
fi
mkdir -p ~/.nip/warehouse/nip
cp /nip/typings.py ~/.config/nip/typings.py
cp /nip/nip ~/.nip/warehouse/nip/nip

