FROM alpine:latest

RUN apk add bash python3 htop openssh
COPY ./ /template

ENTRYPOINT [ "/template/entrypoint.sh"]
