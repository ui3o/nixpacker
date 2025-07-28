FROM docker.io/nixos/nix:latest AS builder

ARG GIT_TAG
WORKDIR /root

COPY ./builder.py /root

RUN export PATH=~/.nix-profile/bin:$PATH
RUN echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf
RUN echo "filter-syscalls = false" >> /etc/nix/nix.conf
RUN nix-env -iA nixpkgs.python3 && nix-env -iA nixpkgs.dpkg
RUN python3 /root/builder.py


FROM alpine:latest
RUN apk add bash && mkdir /warehouse -p /.warehouse/nip
COPY --from=builder /tmp/nix/store /.warehouse
COPY --from=builder /root/*.info /.warehouse/nip
ENTRYPOINT [ "cp", "-a", "/.warehouse/.", "/warehouse"]
