{
  description = "A very basic flake";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
  let inherit (flake-utils.lib) allSystems eachSystem mkApp; in
  eachSystem allSystems (system: 
  let  pkgs = nixpkgs.legacyPackages.${system}; in
  rec {
    packages.simple = pkgs.poetry2nix.mkPoetryApplication { projectDir = ./.; python = pkgs.python39; };
    defaultPackage = packages.simple;
    apps.simple = mkApp { drv = packages.simple; };
    defaultApp = apps.simple;
  });
}
