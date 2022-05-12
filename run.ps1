# Build the ressource file and run the app

$ErrorActionPreference = 'Stop'

Write-Host ("# Building Ressources...") -ForegroundColor Cyan
. pyside6-rcc  "$(Get-ChildItem .\qml\qml.qrc)" -o "$(Get-ChildItem .\qml\qml.qrc)\qrc_qml.py" 

$? ? (Write-Host ("->Done.") -ForegroundColor Green) : (Write-Error ("App finished unnormay.. Last exit code: $LASTEXITCODE")) 

Write-Host ("# Starting the app...") -ForegroundColor Cyan
$app = Start-Process -FilePath "python" -ArgumentList "$(Get-ChildItem .\mode_s\main.py)", "$args" -WorkingDirectory "$(Get-Location)" -NoNewWindow -PassThru -Wait

$? ? (Write-Host ("App existed normally.") -ForegroundColor Green) : (Write-Error ("App finished unnormay.. Last exit code: $LASTEXITCODE")) 
exit $LASTEXITCODE
