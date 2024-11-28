# nixpacker
Build nix package into docker image

# install

`curl -fsSL https://raw.githubusercontent.com/ui3o/nixpacker/refs/heads/main/nip/nip | NIP_INSTALL=true bash`

# build steps

* check available package on this site: https://lazamar.co.uk/nix-versions
  * Note: check `nixpkgs-unstable` and `nixpkgs-x.x-darwin` (where x.x is the highest) channel that the same version is also available
* create a new git tag like this: `hello--2.10`

# run steps
* `podman run --rm -v $HOME/.nix:/nix -it docker.io/ui3o/nixpacker:hello--2.10` this step copy the nix store to the shared volume

