# Build the ressource file and run the app

$ErrorActionPreference = 'Stop'

if ("-t" -notin $args -and "-i" -notin $args) {
    Write-Host ("# Building Ressources...") -ForegroundColor Cyan
    . pyside6-rcc  "$(Get-ChildItem .\qml\qml.qrc)" -o "$(Get-Location)\qml\qrc_qml.py" 
    $? ? (Write-Host ("->Done.") -ForegroundColor Green) : (Write-Error ("App finished unnormay.. Last exit code: $LASTEXITCODE")) 
}


Write-Host ("# Starting the app...") -ForegroundColor Cyan
$app = Start-Process -FilePath "python" -ArgumentList "$(Get-ChildItem .\mode_s\mode_s.py)", "$args" -WorkingDirectory "$(Get-Location)" -NoNewWindow -PassThru -Wait

$? ? (Write-Host ("App existed normally.") -ForegroundColor Green) : (Write-Error ("App finished unnormay.. Last exit code: $LASTEXITCODE")) 
exit $LASTEXITCODE
