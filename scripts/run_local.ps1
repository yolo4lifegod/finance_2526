param(
  [string]$BaseUrl = "http://127.0.0.1:5000"
)

$venvDir = ".venv"
$pythonExe = "python"

if (-not (Test-Path $venvDir)) {
  Write-Output "Creating virtualenv in $venvDir..."
  & $pythonExe -m venv $venvDir
}

$pip = Join-Path $venvDir "Scripts\pip.exe"
$py = Join-Path $venvDir "Scripts\python.exe"

Write-Output "Installing requirements (this may take a moment)..."
& $pip install --upgrade pip
if (Test-Path "requirements.txt") {
  & $pip install -r requirements.txt
}

$env:FLASK_APP = 'run.py'

Write-Output "Starting Flask dev server..."
$proc = Start-Process -FilePath $py -ArgumentList 'run.py' -WindowStyle Hidden -PassThru

Try {
  $timeout = 30
  $started = $false
  $start = Get-Date
  while (-not $started) {
    Start-Sleep -Seconds 1
    if ((Test-NetConnection -ComputerName '127.0.0.1' -Port 5000).TcpTestSucceeded) {
      $started = $true
      break
    }
    if ((Get-Date) - $start -gt (New-TimeSpan -Seconds $timeout)) {
      throw "Server did not start within $timeout seconds"
    }
  }
  Write-Output "Server started (PID $($proc.Id)). Running smoke test..."
  & $py .\scripts\test_purchase_request.py --base-url $BaseUrl
  $rc = $LASTEXITCODE
  Write-Output "Smoke test finished with exit code $rc"
}
Catch {
  Write-Error $_
  $rc = 2
}
Finally {
  if ($proc -and -not $proc.HasExited) {
    Write-Output "Stopping server (PID $($proc.Id))..."
    Stop-Process -Id $proc.Id -Force
  }
}
exit $rc