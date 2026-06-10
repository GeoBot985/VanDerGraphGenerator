$ErrorActionPreference = "Stop"

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build\dist, build\build, dist, user_data
