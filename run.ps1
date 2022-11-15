# Build the ressource file and run the app

$ErrorActionPreference = 'Stop'


if ("-t" -notin $args -and "-i" -notin $args) {
    $qmlFiles = Get-ChildItem .\mode_s\gui\* -Recurse -Include *.qml, *.js | Select-Object -ExpandProperty FullName
    $ressourcesFile = "$(Get-Item .\mode_s\gui\gui.qrc)"
    
    if ("-nl" -notin $args) {
        Write-Host ("# Linting QML...") -ForegroundColor Cyan -NoNewline
        if (Test-Path "D:\Programs\Qt\Qt\5.15.2\msvc2019_64\bin\qmllint.exe") {
            . D:\Programs\Qt\Qt\5.15.2\msvc2019_64\bin\qmllint.exe $qmlFiles --check-unqualified 
            if (-not $LASTEXITCODE) {
                Write-Host ("`t`t`tDone.") -ForegroundColor Green
            } else {
                Write-Host ("Warnings... Last exit code: $LASTEXITCODE") -ForegroundColor DarkYellow
            }          
        } 

    } 

    Write-Host ("# Building Ressources...") -ForegroundColor Cyan -NoNewline
    . pyside2-rcc  $ressourcesFile -o "$(Get-Location)\mode_s\gui\qrc_gui.py" 
    if (-not $LASTEXITCODE) {
        Write-Host ("`t`t`tDone.") -ForegroundColor Green
    }
    else {
        Write-Host ("Warnings... Last exit code: $LASTEXITCODE") -ForegroundColor DarkYellow
    }          
}


Write-Host ("# Starting the app...") -ForegroundColor Cyan
$app = Start-Process -FilePath "python" -ArgumentList "$(Get-ChildItem .\mode_s\mode_s.py)", "$($args | Where-Object {$_ -ne "-nl" -and $_ -ne "--loop"})" -WorkingDirectory "$(Get-Location)" -NoNewWindow -PassThru -Wait

if (-not $LASTEXITCODE) {
    Write-Host ("`t`t`tDone.") -ForegroundColor Green
}
else {
    Write-Host ("Warnings... Last exit code: $LASTEXITCODE") -ForegroundColor DarkYellow
}          
exit $LASTEXITCODE
