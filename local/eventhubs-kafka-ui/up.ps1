$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

docker info --format "{{.ServerVersion}}" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker is not running."
    exit 1
}

$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Error "Missing .env. Copy .env.example to .env and set EVENTHUB_CONNECTION_STRING."
    exit 1
}

$text = [System.IO.File]::ReadAllText($envFile)
$match = [regex]::Match($text, '(?m)^EVENTHUB_CONNECTION_STRING=(.*)$')
$value = if ($match.Success) { $match.Groups[1].Value.Trim() } else { "" }
if ($value.Length -eq 0 -or $value -match 'REPLACE_ME|REPLACE_WITH') {
    Write-Error "EVENTHUB_CONNECTION_STRING is empty. Fill local/eventhubs-kafka-ui/.env only."
    exit 1
}
if ($value.StartsWith("sb://") -and $value.Contains("SharedAccessKeyName=") -and $value.Contains("SharedAccessKey=")) {
    $value = "Endpoint=" + $value
    $updated = [regex]::Replace($text, '(?m)^EVENTHUB_CONNECTION_STRING=.*$', "EVENTHUB_CONNECTION_STRING=$value")
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($envFile, $updated, $utf8)
}

docker compose up -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output "UI http://127.0.0.1:8080"
Write-Output "Cluster dev-visitvn-evhns-sg-01"
