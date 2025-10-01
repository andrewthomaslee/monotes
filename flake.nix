{
  description = "Using Nix Flake apps to run scripts with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    ...
  }: let
    inherit (nixpkgs) lib;

    # Create attrset for each system
    forAllSystems = lib.genAttrs ["x86_64-linux" "aarch64-linux"];

    # Workspace and package setup
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};

    overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel";
    };

    pythonSets = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (pkgs.stdenv) mkDerivation;
        python = pkgs.python313;
        baseSet = pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        };
      in
        baseSet.overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
            (final: prev: {
              monotes = prev.monotes.overrideAttrs (old: {
                passthru =
                  (old.passthru or {})
                  // {
                    tests = let
                      virtualenv = final.mkVirtualEnv "monotes-venv-tests" {
                        monotes = ["dev"];
                      };
                    in
                      (old.tests or {})
                      // {
                        pytest = mkDerivation {
                          name = "${final.monotes.name}-pytest";
                          inherit (final.monotes) src;
                          nativeBuildInputs = [virtualenv];
                          dontConfigure = true;
                          buildPhase = ''
                            runHook preBuild
                            pytest --cov tests --cov-report html tests
                            runHook postBuild
                          '';
                          installPhase = ''
                            runHook preInstall
                            mv htmlcov $out
                            runHook postInstall
                          '';
                        };
                        pyrefly = mkDerivation {
                          name = "${final.monotes.name}-pyrefly";
                          inherit (final.monotes) src;
                          nativeBuildInputs = [virtualenv];
                          dontConfigure = true;
                          dontInstall = true;
                          buildPhase = ''
                            runHook preBuild
                            mkdir $out
                            pyrefly check --debug-info $out/pyrefly.json --output-format json --config pyproject.toml
                            runHook postBuild
                          '';
                        };
                        ruff = mkDerivation {
                          name = "${final.monotes.name}-ruff";
                          inherit (final.monotes) src;
                          nativeBuildInputs = [virtualenv];
                          dontConfigure = true;
                          buildPhase = ''
                            runHook preBuild
                            ruff check --ignore F401 --output-format json -o ruff.json
                            runHook postBuild
                          '';
                          installPhase = ''
                            runHook preInstall
                            mv ruff.json $out
                            runHook postInstall
                          '';
                        };
                      };
                  };
              });
            })
          ]
        )
    );
  in {
    packages = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonSet = pythonSets.${system};
      venv = pythonSet.mkVirtualEnv "monotes-venv" workspace.deps.default;
      # alpine base docker image
      alpine = pkgs.dockerTools.pullImage {
        imageName = "alpine";
        imageDigest = "sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1";
        finalImageName = "alpine";
        finalImageTag = "3.22.1";
        sha256 =
          if system == "x86_64-linux"
          then "sha256-oBoU1GqTLZGH8N3TJKoQCjmpkefCzhHFU3DU5etu7zc="
          else if system == "aarch64-linux"
          then "sha256-3jZHiOLGLVzQHalBQ/9Ir+jPqB31Ybvxmv2VHPgwQ+g="
          else throw "Unsupported system: ${system}";
        os = "linux";
        arch =
          if system == "x86_64-linux"
          then "amd64"
          else if system == "aarch64-linux"
          then "arm64"
          else throw "Unsupported system: ${system}";
      };
      monotes-package = pkgs.stdenv.mkDerivation {
        name = "monotes-package";
        src = ./.;
        buildInputs = [venv];
        nativeBuildInputs = with pkgs; [tailwindcss_4];
        installPhase = ''
          mkdir -p $out/app
          cp -r $src/app/* $out/app/

          chmod +w $out/app/style
          tailwindcss -i $src/app/style/input.css -o $out/app/style/output.css --minify
          chmod -w $out/app/style

          cp $src/main.py $out/main
          chmod +x $out/main
          patchShebangs $out/main
        '';
      };
    in {
      default = monotes-package;
      monotes-container = pkgs.dockerTools.buildLayeredImage {
        name = "monotes-container";
        created = "now";
        fromImage = alpine;
        maxLayers = 125;
        contents = [pkgs.curl];
        config = {
          Cmd = ["${monotes-package}/main"];
          ExposedPorts = {"7999/tcp" = {};};
          Healthcheck = {
            Test = ["CMD-SHELL" "curl -f http://localhost:7999/health || exit 1"];
          };
        };
      };
    });

    # Dynamic script discovery for .sh and .py files
    apps = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonSet = pythonSets.${system};
        venv = pythonSet.mkVirtualEnv "monotes-venv" workspace.deps.default;
        inherit (pkgs.lib) filterAttrs hasSuffix mapAttrsToList genAttrs;

        # App discovery and creation
        appsBasedir = ./scripts;
        appFiles = filterAttrs (name: type: type == "regular" && (hasSuffix ".sh" name || hasSuffix ".py" name)) (
          builtins.readDir appsBasedir
        );
        appNames = mapAttrsToList (name: _: pkgs.lib.removeSuffix ".sh" (pkgs.lib.removeSuffix ".py" name)) appFiles;

        # Shared build logic for creating executable scripts
        makeExecutable = appName: ''
          mkdir -p $out/bin
          # Determine actual file path (sh takes precedence)
          if [ -f ${appsBasedir}/${appName}.sh ]; then
            cp ${appsBasedir}/${appName}.sh $out/bin/${appName}
          else
            cp ${appsBasedir}/${appName}.py $out/bin/${appName}
          fi
          chmod +x $out/bin/${appName}
          patchShebangs $out/bin/${appName}
        '';

        # Create individual apps
        makeApp = appName: {
          type = "app";
          program = "${pkgs.runCommand appName {buildInputs = [pkgs.bash venv];} (makeExecutable appName)}/bin/${appName}";
          meta = {description = "Run ${appName}";};
        };

        # Generate all script apps
        scriptApps = genAttrs appNames makeApp;
      in
        scriptApps // {default = scriptApps.fastapi-dev;}
    );

    nixosModules = {
      default = {
        config,
        lib,
        pkgs,
        ...
      }: let
        cfg = config.services.monotes;
      in {
        options = {
          services.monotes = {
            enable = lib.mkEnableOption "monotes";
            domain = lib.mkOption {
              type = lib.types.str;
              default = "localhost";
            };
            fake-data = lib.mkOption {
              type = lib.types.enum ["True" "False"];
              default = "False";
            };
          };
        };
        config = lib.mkIf cfg.enable {
          systemd.services.monotes = {
            description = "monotes.service";
            after = ["docker.service"];
            requires = ["docker.service"];
            wantedBy = ["multi-user.target"];

            serviceConfig = let
              monotes-start = pkgs.writeShellApplication {
                name = "monotes-start";
                runtimeInputs = [pkgs.docker];
                text = ''
                  docker stop monotes-container || true
                  docker rm monotes-container || true
                  docker stop monotes-mongo || true
                  docker rm monotes-mongo || true

                  docker network create --driver bridge monotes-network || true

                  docker pull mongo:8.0.13

                  IMAGE_TAG=$(docker load < ${self.packages.${pkgs.system}.monotes-container} | grep -o 'monotes-container:[^ ]*')

                  docker run -d --network monotes-network -v monotes-mongodb:/data/db --name monotes-mongo mongo:8.0.13
                  docker run -d --network monotes-network --name monotes-container --env DB_URI=mongodb://monotes-mongo --env FAKE_DATA=${cfg.fake-data} \
                    --label "traefik.enable=true" \
                    --label "traefik.http.routers.monotes.rule=Host(\`monotes.${cfg.domain}\`)" \
                    --label "traefik.http.routers.monotes.entrypoints=websecure" \
                    --label "traefik.http.routers.monotes.tls=true" \
                    --label "traefik.http.services.monotes.loadbalancer.server.port=7999" \
                    --label "traefik.http.services.monotes.loadbalancer.sticky.cookie=true" \
                    --label "traefik.http.services.monotes.loadbalancer.sticky.cookie.name=sticky_cookie" \
                    --label "traefik.http.services.monotes.loadbalancer.sticky.cookie.secure=true" \
                    --label "traefik.http.services.monotes.loadbalancer.sticky.cookie.httpOnly=true" \
                  "$IMAGE_TAG"
                '';
              };
              monotes-stop = pkgs.writeShellApplication {
                name = "monotes-stop";
                runtimeInputs = [pkgs.docker];
                text = ''
                  docker stop monotes-container || true
                  docker stop monotes-mongo || true

                  docker rm monotes-container || true
                  docker rm monotes-mongo || true

                  docker network rm monotes-network || true
                '';
              };
            in {
              Type = "oneshot";
              RemainAfterExit = true;
              TimeoutStartSec = "90s";
              RestartSec = "30s";
              User = "root";
              Group = "docker";
              Restart = "on-failure";
              ExecStart = "${monotes-start}/bin/monotes-start";
              ExecStop = "${monotes-stop}/bin/monotes-stop";
            };
          };
        };
      };
    };

    # devShells
    devShells = forAllSystems (system: let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
      python = pkgs.python313;
      pythonSet = pythonSets.${system};
      venv = pythonSet.mkVirtualEnv "monotes-dev-venv" workspace.deps.all;
      # tmux.conf file
      tmuxConf = pkgs.writeText "tmux.conf" ''
        set -g mouse on
        set-option -g default-command "${pkgs.bash}/bin/bash -l"
      '';
      # wrapper script for tmux
      wrappedTmux = pkgs.writeShellScriptBin "tmux" ''
        exec ${pkgs.tmux}/bin/tmux -f ${tmuxConf} "$@"
      '';
      # Packages to install in devShells
      devPackages = with pkgs;
        [
          bash
          jq
          uv
          tailwindcss_4
          watchman
          posting
          mitmproxy
          duckdb
          pyrefly
          ruff
          yazi
          lazydocker
          brave
          firefox
          chromium
          docker
          docker-compose
          docker-buildx
          docker-vackup
        ]
        ++ (lib.optionals (system != "aarch64-linux") [mongodb-compass])
        ++ [wrappedTmux];
    in {
      # This devShell simply adds Python & uv and undoes the dependency leakage done by Nixpkgs Python infrastructure.
      impure = pkgs.mkShell {
        packages =
          [
            python
          ]
          ++ devPackages;
        env =
          {
            UV_PYTHON_DOWNLOADS = "never";
            UV_PYTHON = python.interpreter;
          }
          // lib.optionalAttrs pkgs.stdenv.isLinux {
            LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
          };
        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
          export COMPOSE_BAKE=true
          export SELL=$(which bash)
          export BROWSER=$(which chromium)
          uv sync --directory $REPO_ROOT
          source $REPO_ROOT/.venv/bin/activate
        '';
      };
      # This devShell uses uv2nix to construct a virtual environment purely from Nix, using the same dependency specification as the application.
      default = pkgs.mkShell {
        packages =
          [
            venv
          ]
          ++ devPackages;
        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };
        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
          export COMPOSE_BAKE=true
          export SELL=$(which bash)
          export BROWSER=$(which chromium)
          export VIRTUAL_ENV=${venv}
          source ${venv}/bin/activate
          nix run $REPO_ROOT#vscode
        '';
      };
    });

    # Construct flake checks from Python set
    checks = forAllSystems (system: let
      pythonSet = pythonSets.${system};
    in {
      inherit (pythonSet.monotes.passthru.tests) pytest pyrefly ruff;
    });

    formatter = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in
        pkgs.alejandra
    );
  };
}
