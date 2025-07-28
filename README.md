# nixpacker
Build nix package into docker image

# install

1. install nip: ```podman run -it --rm -v $HOME:/root:Z ui3o/nixpacker:nip```
2. add nip to path: ```export PATH="/nix/store/nip:$HOME/.nip/warehouse/nip:$PATH"```


# build steps

* check available package on this site: https://lazamar.co.uk/nix-versions
* create a new git tag:
  * for new release create please use tag generator page: https://ui3o.github.io/nixpacker/

# usage

1. edit file in ```~/.config/nip/config.py```
2. run ```nip``` 
3. recommended warehouse browsing: `ls -1 .nip/warehouse | fzf`

original:
 * **/nix/store/item-a** =use=> **/nix/store/item-b**

new: 
 * /nix/store/item-a =linked=> **/nix/warehouse/item-a** =use=> /nix/store/item-b =linked=> **/nix/warehouse/item-b**

generation: 
 * /nix/store =linked=> /nix/generations/checksum/store

default override:
 * /nix/store/item-a-v2 =linked=> /nix/store/item-a-v1
 * /nix/store/item-a-v1 =linked=> **/nix/warehouse/item-a**




