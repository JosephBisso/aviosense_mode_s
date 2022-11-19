FROM python:3.7.7-windowsservercore-1809

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

RUN c:\python\python.exe -m pip install --upgrade pip
RUN pip install pyinstaller

SHELL ["cmd", "/S", "/C"]
RUN powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
RUN choco install -y git vim mysql

ENTRYPOINT ["powershell", "-NoLogo", "-ExecutionPolicy", "Bypass"]
