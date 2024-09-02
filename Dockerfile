FROM docker.io/fedora:latest as builder

ARG GIT_TAG
ARG CERTS
RUN awk -v t="$CERTS" 'BEGIN{print t}' >> /etc/pki/ca-trust/source/anchors/mycert.pem && update-ca-trust

RUN echo install nix... && \
    curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install linux --no-confirm --init none --extra-conf "filter-syscalls = false"
RUN . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh

WORKDIR /root

COPY ./src/flake.nix /root
COPY ./src/flake.creator.py /root
COPY ./versions.json /root

ENV VERSION_FILE=/root/versions.json
ENV FLAKE_FILE=/root/flake.nix

RUN /root/.nix-profile/bin/nix-env -iA dpkg -f https://github.com/NixOS/nixpkgs/archive/refs/heads/nixpkgs-unstable.tar.gz
RUN /root/.nix-profile/bin/nix-env -iA python3 -f https://github.com/NixOS/nixpkgs/archive/refs/heads/nixpkgs-unstable.tar.gz

RUN /root/.nix-profile/bin/python3 /root/flake.creator.py
RUN /root/.nix-profile/bin/nix bundle --bundler github:NixOS/bundlers#toDEB -o debpack /root/flake.nix
RUN /root/.nix-profile/bin/dpkg -x /root/debpack/hello_*.deb  /tmp


FROM alpine:latest
COPY --from=builder /tmp/nix /nix
COPY --from=builder /root/pack.info /
ENTRYPOINT [ "sleep", "inf" ]
