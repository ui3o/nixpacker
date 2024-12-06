FROM docker.io/nixos/nix:latest AS builder

ARG GIT_TAG
WORKDIR /root

COPY ./src/builder.py /root
COPY ./tag.info.json /root

RUN export PATH=~/.nix-profile/bin:$PATH
RUN echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf
RUN echo "filter-syscalls = false" >> /etc/nix/nix.conf
RUN nix-env -iA nixpkgs.python3 && nix-env -iA nixpkgs.dpkg
RUN python3 /root/builder.py


FROM alpine:latest
RUN apk add python3
COPY --from=builder /tmp/nix /.nix
COPY --from=builder /root/*.info /.nix
COPY ./src/entrypoint.py /entrypoint.py
ENTRYPOINT [ "python3", "/entrypoint.py"]
