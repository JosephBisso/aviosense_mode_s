@echo off

set arg1=%1

if "%arg1%"=="--loop" goto loop
goto launch

:loop
set /p input="Start ?[y/n]"
if "%input%"=="n" goto end
cls
goto launch

:launch
pwsh .\run.ps1 %*
if "%arg1%"=="--loop" goto loop
goto end

:end
exit %ErrorLevel%
