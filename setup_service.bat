@echo off
echo Installing Clipbridge Service...

REM Get the current directory (where Clipbridge is installed)
set INSTALL_DIR=%~dp0
set INSTALL_DIR=%INSTALL_DIR:~0,-1%

echo Install Directory: %INSTALL_DIR%

REM Stop service if it exists
echo Stopping existing service (if any)...
"%INSTALL_DIR%\nssm\nssm.exe" stop Clipbridge >nul 2>&1

REM Remove existing service
echo Removing existing service (if any)...
"%INSTALL_DIR%\nssm\nssm.exe" remove Clipbridge confirm >nul 2>&1

REM Install the service
echo Installing Clipbridge service...
"%INSTALL_DIR%\nssm\nssm.exe" install Clipbridge "%INSTALL_DIR%\python\python.exe" "%INSTALL_DIR%\clipbridge.py" --service

REM Configure the service
echo Configuring service...
"%INSTALL_DIR%\nssm\nssm.exe" set Clipbridge AppDirectory "%INSTALL_DIR%"
"%INSTALL_DIR%\nssm\nssm.exe" set Clipbridge DisplayName "Clipbridge - iPhone to PC Clipboard Bridge"
"%INSTALL_DIR%\nssm\nssm.exe" set Clipbridge Description "HTTP service that bridges clipboard between iPhone and Windows PC"
"%INSTALL_DIR%\nssm\nssm.exe" set Clipbridge Start SERVICE_AUTO_START

REM Set up logging
"%INSTALL_DIR%\nssm\nssm.exe" set Clipbridge AppStdout "%INSTALL_DIR%\logs\clipbridge.log"
"%INSTALL_DIR%\nssm\nssm.exe" set Clipbridge AppStderr "%INSTALL_DIR%\logs\clipbridge_error.log"

REM Create logs directory
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"

REM Start the service
echo Starting Clipbridge service...
"%INSTALL_DIR%\nssm\nssm.exe" start Clipbridge

REM Check service status
timeout /t 3 /nobreak >nul
echo.
echo Service Status:
sc query Clipbridge

echo.
echo Clipbridge service has been installed and started!
echo You can now send clipboard data from your iPhone to http://YOUR_PC_IP:5019/clip
echo.
echo To find your PC's IP address, run: ipconfig
echo.
pause
