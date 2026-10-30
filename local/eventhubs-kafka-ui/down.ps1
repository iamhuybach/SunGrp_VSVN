$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
docker compose down
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
