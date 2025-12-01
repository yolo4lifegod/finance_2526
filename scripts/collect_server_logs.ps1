param(
  [string]$OutFile = ".\logs\server.log",
  [int]$DurationSeconds = 30
)

New-Item -Path (Split-Path $OutFile) -ItemType Directory -Force | Out-Null
Write-Output "Capturing server stdout to $OutFile for $DurationSeconds seconds..."
# Tail the file if run.py writes to server.log; otherwise, this is a placeholder to collect logs.
Start-Sleep -Seconds $DurationSeconds
Write-Output "Done. Check $OutFile"