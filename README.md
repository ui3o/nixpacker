# nixpacker
Build nix package into docker image

* for new release create please use tag generator page: https://ui3o.github.io/nixpacker/

# install

* `podman run --rm -v $HOME/.config:/root/.config -v $HOME/.nix:/nix -it docker.io/ui3o/nixpacker:nip`

original:
 * **/nix/store/item-a** =use=> **/nix/store/item-b**

new: 
 * /nix/store/item-a =linked=> **/nix/warehouse/item-a** =use=> /nix/store/item-b =linked=> **/nix/warehouse/item-b**

generation: 
 * /nix/store =linked=> /nix/generations/checksum/store

default override:
 * /nix/store/item-a-v2 =linked=> /nix/store/item-a-v1
 * /nix/store/item-a-v1 =linked=> **/nix/warehouse/item-a**


# build steps

* check available package on this site: https://lazamar.co.uk/nix-versions
  * Note: check `nixos-x.x` and `nixpkgs-x.x-darwin` (where x.x is any) channel that the same version is also available
* create a new git tag like this: `hello--2.10`

# run steps
* `podman run --rm -v $HOME/.nix:/nix -it docker.io/ui3o/nixpacker:hello--2.10` this step copy the nix store to the shared volume

