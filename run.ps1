# Build the ressource file and run the app

$ErrorActionPreference = 'Stop'

Write-Host ("# Building Ressources...") -ForegroundColor Cyan
. pyside6-rcc "D:\BA\ba_mode-s_analysis\qml\qml.qrc" -o "D:\BA\ba_mode-s_analysis\qml\qrc_qml.py" 

$? ? (Write-Host ("->Done.") -ForegroundColor Green) : (Write-Error ("App finished unnormay.. Last exit code: $LASTEXITCODE")) 

Write-Host ("# Starting the app...") -ForegroundColor Cyan
$app = Start-Process -FilePath "python" -ArgumentList "D:\BA\ba_mode-s_analysis\mode_s\main.py" -WorkingDirectory "D:\BA\ba_mode-s_analysis" -NoNewWindow -PassThru -Wait

$? ? (Write-Host ("App existed normally.") -ForegroundColor Green) : (Write-Error ("App finished unnormay.. Last exit code: $LASTEXITCODE")) 
exit $LASTEXITCODE
