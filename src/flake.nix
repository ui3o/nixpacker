{
  description = "Generic package flake";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/__ref__";
  };

  outputs = { self, nixpkgs }: {
        packages.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.__pack__;
        packages.aarch64-linux.default = nixpkgs.legacyPackages.aarch64-linux.__pack__;
    };
}
