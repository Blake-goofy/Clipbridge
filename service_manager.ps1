# Clipbridge Service Management Script
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("install", "uninstall", "start", "stop", "status")]
    [string]$Action
)

$ServiceName = "Clipbridge"
$ServiceDisplayName = "Clipbridge - iPhone to PC Clipboard Bridge"
$ServiceDescription = "HTTP service that bridges clipboard between iPhone and Windows PC"
$PythonExe = "C:\Users\blake\source\repos\Clipbridge\venv\Scripts\python.exe"
$ScriptPath = "C:\Users\blake\source\repos\Clipbridge\clipbridge.py"
$WorkingDirectory = "C:\Users\blake\source\repos\Clipbridge"

function Install-ClipbridgeService {
    Write-Host "Installing Clipbridge service..." -ForegroundColor Green
    
    # Check if NSSM is available
    $nssm = Get-Command nssm -ErrorAction SilentlyContinue
    if ($nssm) {
        Write-Host "Using NSSM to create service..." -ForegroundColor Yellow
        
        & nssm install $ServiceName $PythonExe $ScriptPath --service
        & nssm set $ServiceName AppDirectory $WorkingDirectory
        & nssm set $ServiceName DisplayName $ServiceDisplayName
        & nssm set $ServiceName Description $ServiceDescription
        & nssm set $ServiceName Start SERVICE_AUTO_START
        
        Write-Host "Service installed successfully!" -ForegroundColor Green
        Write-Host "Run 'Start-Service $ServiceName' to start the service" -ForegroundColor Yellow
    } else {
        Write-Host "NSSM not found. Please install NSSM from https://nssm.cc/download" -ForegroundColor Red
        Write-Host "Alternative: Use Task Scheduler with the provided batch file" -ForegroundColor Yellow
    }
}

function Uninstall-ClipbridgeService {
    Write-Host "Uninstalling Clipbridge service..." -ForegroundColor Green
    
    $nssm = Get-Command nssm -ErrorAction SilentlyContinue
    if ($nssm) {
        & nssm stop $ServiceName
        & nssm remove $ServiceName confirm
        Write-Host "Service uninstalled successfully!" -ForegroundColor Green
    } else {
        Write-Host "NSSM not found. Cannot uninstall service." -ForegroundColor Red
    }
}

function Start-ClipbridgeService {
    Write-Host "Starting Clipbridge service..." -ForegroundColor Green
    Start-Service $ServiceName
    Get-Service $ServiceName
}

function Stop-ClipbridgeService {
    Write-Host "Stopping Clipbridge service..." -ForegroundColor Green
    Stop-Service $ServiceName
    Get-Service $ServiceName
}

function Get-ClipbridgeServiceStatus {
    Write-Host "Clipbridge service status:" -ForegroundColor Green
    Get-Service $ServiceName -ErrorAction SilentlyContinue | Format-Table -AutoSize
    
    # Also check if the HTTP server is responding
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5019" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "HTTP server is responding (404 expected for GET request)" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "HTTP server is responding (404 expected for GET request)" -ForegroundColor Green
        } else {
            Write-Host "HTTP server is not responding" -ForegroundColor Red
        }
    }
}

# Execute the requested action
switch ($Action) {
    "install" { Install-ClipbridgeService }
    "uninstall" { Uninstall-ClipbridgeService }
    "start" { Start-ClipbridgeService }
    "stop" { Stop-ClipbridgeService }
    "status" { Get-ClipbridgeServiceStatus }
}
