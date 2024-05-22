@echo off
REM Pfad zu Applauncher.exe anpassen, falls nötig
set EXE_PATH="..\dist\process\Applauncher.exe"

REM Parameter für das Skript
REM set "URL=https://lb3.pcvisit.de/v1/hosted/jumplink?func=download&topic=guestSetup&destname=pcvisit_Kunden-Modul&os=osWin32"
REM set "PROCESS_NAME=pcvisit"

set "URL=https://url.de/zu.exe"
set "PROCESS_NAME=prozessName"


REM Skript mit den Parametern ausführen
start "" %EXE_PATH% "%URL%" "%PROCESS_NAME%"

exit
