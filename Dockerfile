FROM docker.io/fedora:latest as builder

ARG GIT_TAG
WORKDIR /root

COPY ./src/flake.nix /root
COPY ./src/builder.py /root

ENV FLAKE_FILE=/root/flake.nix

RUN echo install nix... && \
    curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install linux --no-confirm --init none --extra-conf "filter-syscalls = false"

RUN echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf
RUN python3 /root/builder.py


FROM alpine:latest
RUN apk add python3
COPY --from=builder /tmp/nix /.nix
COPY --from=builder /root/*.info /.nix
COPY ./src/entrypoint.py /entrypoint.py
ENTRYPOINT [ "python3", "/entrypoint.py"]
