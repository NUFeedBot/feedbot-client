{
  description = "Flake for FeedBot client";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = { allowUnfree = true; };
        };
        python = pkgs.python312;
        pythonPackages = python.pkgs;

        pythonEnvironment = python.withPackages (ps:
          with ps; [
            requests
            openai
            tiktoken
            python-dotenv
            pyopenssl
          ]);

      in {
        devShells.default = pkgs.mkShell {
          buildInputs =
            [ pkgs.python312 pythonEnvironment pkgs.openssl ];

          shellHook = ''
            source .env

            echo "FeedBot development environment loaded"
            echo "Python version: ${python.version}"
          '';
        };
      });
 }
