FROM python:3.7.7-windowsservercore-1809

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

COPY ./requirements.txt ./requirements.txt
COPY ./lib/GDAL-3.4.2-cp37-cp37m-win_amd64.whl ./GDAL-3.4.2-cp37-cp37m-win_amd64.whl
COPY ./lib/Fiona-1.8.21-cp37-cp37m-win_amd64.whl ./Fiona-1.8.21-cp37-cp37m-win_amd64.whl

RUN c:\python\python.exe -m pip install --upgrade pip

RUN pip install ./GDAL-3.4.2-cp37-cp37m-win_amd64.whl
RUN pip install ./Fiona-1.8.21-cp37-cp37m-win_amd64.whl
RUN pip install -r requirements.txt

RUN pip install pyinstaller

SHELL ["cmd", "/S", "/C"]
RUN powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
RUN choco install -y git


ENTRYPOINT ["powershell", "-NoLogo", "-ExecutionPolicy", "Bypass"]
