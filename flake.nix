{
  description = "Game Budget — LAN allowance kiosk";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { nixpkgs, ... }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
    in
    {
      devShells = nixpkgs.lib.genAttrs supportedSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          pythonEnv = pkgs.python312.withPackages (ps: [ ps.pyyaml ]);
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              pythonEnv
              ledger
              uv
              just
            ];
            shellHook = ''
              echo "Game Budget dev shell"
              echo "  just sync && just init && just run"
              echo "  just docker-up"
            '';
          };
        }
      );
    };
}
