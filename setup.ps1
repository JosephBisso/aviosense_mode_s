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

Write-Host "`n$ Preparing sqldrivers.." -ForegroundColor Cyan
$libs_qsql = Get-Item .\lib\qsql*.dll | Select-Object -ExpandProperty FullName
if (Test-Path .\virtualenv\) {
    $sqldrivers = "$(Get-ChildItem .\virtualenv\ -Directory -Recurse -Include 'sqldrivers')"
    if ($sqldrivers) {
        $libs_qsql | Copy-Item -Destination $sqldrivers
        Write-Host ">> Done" -ForegroundColor Green
    }
} else {
    $python = Get-Command python 
    $py_dir = Get-Item $python.Source
    $sqldrivers = "$(Get-ChildItem $py_dir.Directory -Recurse -Directory -Include "sqldrivers" -ErrorAction SilentlyContinue)"
    if ($sqldrivers) {
        $libs_qsql | Copy-Item -Destination $sqldrivers
        Write-Host ">> Done" -ForegroundColor Green
    }
    else {
        Write-Host ">> Could not prepare sqldrivers" -ForegroundColor Red
        Write-Host "|-> Please copy <lib/qsql*.dll> to <python PySide2 location>/plugins/sqldrivers" -ForegroundColor DarkYellow
        exit -1
    }
}

Write-Host "`n$ Looking for mysql.exe .." -ForegroundColor Cyan
$mysql = Get-Command mysql.exe -ErrorAction SilentlyContinue
if (-not $mysql) {
    Write-Host ">> MySql must be installed AND added to PATH" -ForegroundColor Red
    Write-Host "[ ] Download mysql here 'https://dev.mysql.com/downloads/mysql/'" -ForegroundColor DarkYellow
    Write-Host "[ ] Or install it with choco: 'choco install -y mysql'" -ForegroundColor DarkYellow
    Write-Host "If already installed, add it to the PATH" -ForegroundColor DarkYellow
    exit -1
} else {
    Write-Host ">> Done" -ForegroundColor Green
}

Write-Host "`n`nSUCCESS: Setup completed" -ForegroundColor Green
