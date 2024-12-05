FROM alpine:latest

RUN apk add bash python3 htop openssh
COPY ./ /template
RUN mv /template/nip /template/nip_tmp
RUN mkdir /nix && ln -sf /root/.nix/warehouse /nix/warehouse
RUN ln -sf /root/.config/nip /template/nip

ENTRYPOINT [ "/template/entrypoint.sh"]
