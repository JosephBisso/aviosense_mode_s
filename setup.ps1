# Installing all Dependencies

if ("--venv" -in $args) {
    if (Test-Path .\virtualenv) {
        $deactivate_venv = Get-Command deactivate -ErrorAction SilentlyContinue
        if ($deactivate_venv) {
            Write-Host "[! ] Deactivating active virtual environment" -ForegroundColor DarkGray
            . $deactivate_venv
        }
        Write-Host "[!!] Removing old virtual environment" -ForegroundColor DarkGray
        Remove-Item .\virtualenv -Force -Recurse
    }

    Write-Host "`n[0/2] Creating new virtual python environment" -ForegroundColor Cyan
    python -m venv .\virtualenv
    . .\virtualenv\Scripts\Activate.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ">> Aborting Setup" -ForegroundColor Red
        exit -1
    } else {
        Write-Host ">> Done" -ForegroundColor Green
    }
}

Write-Host "`n[1/2] Installing main dependencies" -ForegroundColor Cyan
pip install -r .\requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host ">> Aborting" -ForegroundColor Red
    exit -1
} else {
    Write-Host ">> Done" -ForegroundColor Green
}

Write-Host "`n[2/2] Checking other dependencies" -ForegroundColor Cyan
Write-Host "$ Installing GDAL.." -ForegroundColor Cyan
pip install .\lib\GDAL-3.4.2-cp37-cp37m-win_amd64.whl
if ($LASTEXITCODE -ne 0) {
    Write-Host ">> Aborting" -ForegroundColor Red
    exit -1
}
else {
    Write-Host ">> Done" -ForegroundColor Green
}

Write-Host "`n`nSUCCESS: Setup completed" -ForegroundColor Green
