# Load .env into current process and start the backend
$envPath = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $envPath) {
  Get-Content $envPath | ForEach-Object {
    if ($_ -match "^\s*#" -or $_ -match "^\s*$") { return }
    $kv = $_ -split "=", 2
    if ($kv.Length -eq 2) {
      [System.Environment]::SetEnvironmentVariable($kv[0], $kv[1], "Process")
    }
  }
} else {
  Write-Host "No .env found at $envPath"
}

Set-Location (Join-Path $PSScriptRoot "..")
python -m uvicorn app.main:app --reload --port 8000