# nixpacker
Build nix package into docker image

# build steps

* check available package on this site: https://lazamar.co.uk/nix-versions
  * Note: check `nixpkgs-unstable` and `nixpkgs-x.x-darwin` (where x.x is the highest) channel that the same version is also available
* create a new git tag like this: `hello--2.10`

# run steps
* `podman run -v share:/share -it docker.io/ui3o/nixpacker:hello--2.10` this step copy the nix store to the shared volume
* `podman run -it -v share:/nix  alpine` this is an example how possible to use nix store in other container
