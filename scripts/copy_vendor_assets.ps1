$ErrorActionPreference = "Stop"

$target = "build/staging/assets/vendor"
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Recurse -Force "assets/vendor/*" $target
