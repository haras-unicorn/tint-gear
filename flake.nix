{
  description = "Warning: tint-gear may cause an uncontrollable urge to redecorate everything.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";

    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... } @rawInputs:
    let
      systems = flake-utils.lib.defaultSystems;
    in
    builtins.foldl'
      (outputs: system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlay = [ poetry2nix.overlay ];
          };
          poetry2nix = (rawInputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; });

          env = poetry2nix.mkPoetryEnv {
            projectDir = ./.;
            preferWheels = true;
          };

          mkEnvWrapper = name: pkgs.writeShellApplication {
            name = name;
            runtimeInputs = [ env ];
            text = ''
              export PYTHONPREFIX=${env}
              export PYTHONEXECUTABLE=${env}/bin/python

              # shellcheck disable=SC2125
              export PYTHONPATH=${env}/lib/**/site-packages

              ${name} "$@"
            '';
          };
        in
        outputs // rec {
          devShells.${system}.default = pkgs.mkShell {
            packages = with pkgs; [
              # Nix
              nil
              nixpkgs-fmt

              # Python
              poetry
              (mkEnvWrapper "pyright")
              (mkEnvWrapper "pyright-langserver")
              env

              # Misc
              nodePackages.prettier
              nodePackages.yaml-language-server
              marksman
              taplo

              # Tools
              nushell
              just
            ];
          };

          apps.${system}.default = {
            type = "app";
            program = "${packages.${system}.default}/bin/tint-gear";
          };

          packages.${system}.default = poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            preferWheels = true;
          };

          lib.colors = { imagePath, args ? { } }:
            let
              image = builtins.path {
                path = imagePath;
                name = "image-path";
              };

              argString = pkgs.lib.concatStringsSep
                " "
                (builtins.attrValues
                  (builtins.mapAttrs
                    (n: v:
                      if (builtins.length n) == 1
                      then "-${n} ${v}"
                      else "--${n} v")
                    (pkgs.lib.filterAttrs
                      (n: v: v != null)
                      (args))));

              result = pkgs.runCommand
                "tint-gear"
                { }
                ''
                  "${packages.${system}.default}/bin/tint-gear" \
                    ${image} \
                    ${argString} \
                    > $out
                '';
            in
            builtins.fromJSON (builtins.readFile result);
        })
      { }
      systems;
}
