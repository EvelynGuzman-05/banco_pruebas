{ pkgs ? import <nixpkgs> {} }:
(pkgs.buildFHSUserEnv {
  name = "pipzone";
  targetPkgs = pkgs: (with pkgs; [
    python314
    uv
    python314Packages.pip
    python314Packages.uv
  ]);
  runScript = "bash --init-file /etc/profile";
}).env

