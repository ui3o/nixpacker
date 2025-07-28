#!/bin/bash

if [ ! -d ~/.config/nip ]; then
    mkdir -p ~/.config/nip
    cp /nip/config.py ~/.config/nip/config.py
fi
cp /nip/typings.py ~/.config/nip/typings.py

mkdir -p ~/.nip/warehouse/nip
cp /nip/config.py ~/.nip/warehouse/nip/config.py
cp /nip/typings.py ~/.nip/warehouse/nip/typings.py
cp /nip/nip ~/.nip/warehouse/nip/nip

