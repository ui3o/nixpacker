#!/bin/bash

[[ -z "${NIP_BASENAME}" ]] && NIP_BASENAME=$(basename "$0")
NIP_CMD="${NIP_BASENAME} $@"
NIP_RUNTIME=podman
NIP_RUN_DEFAULTS="run --network=host --rm --privileged -it --env-file $HOME/.nix/environment"
NIP_RUN_DEFAULTS="${NIP_RUN_DEFAULTS} -v $HOME:$HOME -v $HOME:$HOME --mount=type=bind,source=$HOME/.nix/passwd,destination=/etc/passwd"
[[ $PWD == $HOME* ]] && NIP_RUN_DEFAULTS="${NIP_RUN_DEFAULTS} --workdir $PWD"
NIP_IMAGE="docker.io/ui3o/nixpacker:nip"
[ -f ~/.config/nip/.bashrc ] && source ~/.config/nip/.bashrc

[ ! -f ~/.ssh/id_rsa ] && ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""
[ ! -f ~/.ssh/nip/authorized_keys ] && mkdir -p ~/.ssh/nip && cp  ~/.ssh/id_rsa.pub  ~/.ssh/nip/authorized_keys
[ ! -f ~/.ssh/nip/sshd_config ] && \
    $NIP_RUNTIME $NIP_RUN_DEFAULTS -v $HOME:/root --entrypoint cp $NIP_IMAGE /template/sshd_config /root/.ssh/nip/sshd_config
/usr/sbin/sshd -h ~/.ssh/id_rsa -f $HOME/.ssh/nip/sshd_config

[ ! -d ~/.nix ] && mkdir -p ~/.nix && echo "root:x:0:0:root:$HOME:/bin/sh" > ~/.nix/passwd 
env > ~/.nix/environment
echo "PATH=$PATH" > ~/.ssh/environment
echo "USER=root" >> ~/.nix/environment
echo "OS_USER=$USER" >> ~/.nix/environment
[[ ! -z "${NIP_DEBUG}" ]] && NIP_RUN_DEFAULTS="${NIP_RUN_DEFAULTS} --entrypoint bash"
[[ ! -z "${NIP_DEBUG}" ]] && NIP_CMD=""
$NIP_RUNTIME $NIP_RUN_DEFAULTS $NIP_EXTRA $NIP_IMAGE $NIP_CMD
