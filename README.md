# nixpacker
Build nix package into docker image

# build steps

* create a new git tag like this: `hello@2.10`

# run steps
* `podman run -v share:/share -it docker.io/ui3o/nixpacker:hello@2.10` this step copy the nix store to the shared volume
* `podman run -it -v share:/nix  alpine` this is an example how possible to use nix store in other container
