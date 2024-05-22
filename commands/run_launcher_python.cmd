@echo off
REM Pfad zu Python-Installation anpassen, falls nötig
set PYTHON_PATH="C:\Program Files\Python312\python.exe"

REM Pfad zu launcher.py anpassen, falls nötig
set SCRIPT_PATH=".\launcher.py"

REM Parameter für das Skript
REM set "URL=https://lb3.pcvisit.de/v1/hosted/jumplink?func=download&topic=guestSetup&destname=pcvisit_Kunden-Modul&os=osWin32"
REM set "PROCESS_NAME=pcvisit"

set "URL=https://url.de/zu.exe"
set "PROCESS_NAME=prozessName"

REM Skript mit den Parametern ausführen
%PYTHON_PATH% %SCRIPT_PATH% "%URL%" "%PROCESS_NAME%"
