@echo off

set arg1=%1

if "%arg1%"=="--loop" goto loop
goto launch

:loop
timeout /t -1
cls
echo run.bat %*
goto launch 

:launch
powershell .\run.ps1 %*
if "%arg1%"=="--loop" goto loop
goto end

:end
exit %ErrorLevel%
