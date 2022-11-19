# Lint, build the ressource file and run the app

$ErrorActionPreference = 'Stop'

function Start-ModeS($arguments) {    
    Write-Host ("run.ps1 $arguments`n") -ForegroundColor DarkGray

    if ("-t" -notin $arguments -and "-i" -notin $arguments) {
        $qmlFiles = Get-ChildItem .\src\gui\* -Recurse -Include *.qml, *.js | Select-Object -ExpandProperty FullName
        $ressourcesFile = "$(Get-Item .\src\gui\gui.qrc)"
        
        Write-Host ("# Linting QML...") -ForegroundColor Cyan -NoNewline
        $qmllint = Get-Command qmllint.exe -ErrorAction SilentlyContinue
        if ($qmllint) {
            . $qmllint $qmlFiles --check-unqualified 
            if ($LASTEXITCODE -eq 0) {
                Write-Host ("`tDone.") -ForegroundColor Green
            }
            else {
                Write-Host ("Warnings... Last exit code: $LASTEXITCODE") -ForegroundColor DarkYellow
            }         
        }
        else {
            Write-Host ("`tSkipped`n|-> Cannot find qmllint.exe") -ForegroundColor DarkYellow
        }
    
    
        Write-Host ("# Building Ressources...") -ForegroundColor Cyan -NoNewline
        $pyside2_rcc = Get-Command pyside2-rcc.exe -ErrorAction SilentlyContinue
        if ($pyside2_rcc) {
            . $pyside2_rcc  $ressourcesFile -o "$(Get-Location)\src\gui\qrc_gui.py" 
            if ($LASTEXITCODE -eq 0) {
                Write-Host ("`tDone.") -ForegroundColor Green
            }
            else {
                Write-Host ("Warnings... Last exit code: $LASTEXITCODE") -ForegroundColor DarkYellow
            }          
        }
        else {
            Write-Host ("`tError`n|->Cannot find pyside2_rcc.exe") -ForegroundColor Red
        }
    }
    
    
    Write-Host ("# Starting the app...") -ForegroundColor Cyan
    
    $app = Start-Process -FilePath "python" -ArgumentList "$(Get-Item .\src\app\main.py)", "$($arguments | Where-Object {$_ -ne "--loop"})" -WorkingDirectory "$(Get-Location)/src" -NoNewWindow -PassThru -Wait
    if ($app.ExitCode -eq 0) {
        Write-Host ("`tDone.") -ForegroundColor Green
    } else {
        Write-Host ("Warnings... Last exit code: $($app.ExitCode)") -ForegroundColor DarkYellow
    }         
}

if ("--loop" -in $args) {
    while($True) {
        $continue = Read-Host -Prompt "Press [enter] to continue or [n] to stop"
        if ($continue -eq 'n') {break}
        Clear-Host
        Start-ModeS $args
    }
} else {
    Start-ModeS $args
}

Write-Host "Run.ps1 finished" -ForegroundColor DarkGray
exit $LASTEXITCODE
