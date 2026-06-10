$ErrorActionPreference = "Stop"

if (-not (Test-Path "dist/VanDerGraphGenerator/VanDerGraphGenerator.exe")) {
    throw "Packaged executable not found. Run scripts/build_exe.ps1 first."
}

& "dist/VanDerGraphGenerator/VanDerGraphGenerator.exe" --smoke-test
