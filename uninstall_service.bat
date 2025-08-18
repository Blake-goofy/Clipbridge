@echo off
echo Uninstalling Clipbridge Service...

REM Get the current directory
set INSTALL_DIR=%~dp0
set INSTALL_DIR=%INSTALL_DIR:~0,-1%

echo Install Directory: %INSTALL_DIR%

REM Stop the service
echo Stopping Clipbridge service...
"%INSTALL_DIR%\nssm\nssm.exe" stop Clipbridge

REM Wait a moment for service to stop
timeout /t 3 /nobreak >nul

REM Remove the service
echo Removing Clipbridge service...
"%INSTALL_DIR%\nssm\nssm.exe" remove Clipbridge confirm

echo.
echo Clipbridge service has been uninstalled.
echo.
pause
