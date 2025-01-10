FROM alpine:latest

RUN apk add bash python3 htop openssh lsof curl ca-certificates util-linux
COPY ./ /template
RUN mv /template/nip /template/nip_tmp && ln -sf /nip_cfg /template/nip
RUN mkdir /nix && rm -rf /root

ENTRYPOINT [ "/template/entrypoint.sh"]
