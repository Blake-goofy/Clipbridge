# Clipbridge Service Installation Guide

## Quick Setup (Recommended - NSSM Method)

### Step 1: Download NSSM
1. Go to https://nssm.cc/download
2. Download the latest version
3. Extract `nssm.exe` to `C:\nssm\` (or any folder in your PATH)

### Step 2: Install Service (Run as Administrator)
```powershell
# Navigate to the Clipbridge directory
cd "C:\Users\blake\source\repos\Clipbridge"

# Install the service
C:\nssm\nssm.exe install Clipbridge "C:\Users\blake\source\repos\Clipbridge\venv\Scripts\python.exe" "C:\Users\blake\source\repos\Clipbridge\clipbridge.py" --service

# Set working directory
C:\nssm\nssm.exe set Clipbridge AppDirectory "C:\Users\blake\source\repos\Clipbridge"

# Set service to auto-start
C:\nssm\nssm.exe set Clipbridge Start SERVICE_AUTO_START

# Set service description
C:\nssm\nssm.exe set Clipbridge Description "iPhone to PC Clipboard Bridge Service"

# Start the service
C:\nssm\nssm.exe start Clipbridge
```

### Step 3: Verify Service
```powershell
# Check service status
Get-Service Clipbridge

# Test the HTTP endpoint
Invoke-WebRequest -Uri "http://localhost:5019" -Method GET
# (Should return 404, which means the server is running)
```

## Alternative Method: Task Scheduler

### Step 1: Create Task
1. Open Task Scheduler as Administrator
2. Create Basic Task...
3. Name: "Clipbridge Service"
4. Trigger: "When the computer starts"
5. Action: "Start a program"
6. Program: `C:\Users\blake\source\repos\Clipbridge\start_clipbridge_service.bat`

### Step 2: Configure Task
1. Right-click the task → Properties
2. General tab: Check "Run whether user is logged on or not"
3. General tab: Check "Run with highest privileges"
4. Settings tab: Check "Run task as soon as possible after a scheduled start is missed"

## Service Management Commands

### Using NSSM:
```powershell
# Start service
nssm start Clipbridge

# Stop service
nssm stop Clipbridge

# Restart service
nssm restart Clipbridge

# Remove service
nssm remove Clipbridge

# View service status
nssm status Clipbridge
```

### Using Windows Service Manager:
```powershell
# Start service
Start-Service Clipbridge

# Stop service
Stop-Service Clipbridge

# Get service status
Get-Service Clipbridge
```

## Troubleshooting

### Check Service Logs
- NSSM logs are typically in: `C:\Windows\System32\config\systemprofile\AppData\Local\Temp\`
- Look for files named `Clipbridge_*.log`

### Test Manual Start
```powershell
# Activate virtual environment and test
cd "C:\Users\blake\source\repos\Clipbridge"
.\venv\Scripts\Activate.ps1
python clipbridge.py --service
```

### Common Issues
1. **Service won't start**: Check that Python path and script path are correct
2. **HTTP server not accessible**: Check Windows Firewall settings for port 5019
3. **Virtual environment issues**: Ensure all dependencies are installed in the venv

## iPhone Shortcut Setup
Once the service is running, use these URLs in your iPhone shortcuts:
- Text: `http://YOUR_PC_IP:5019/clip` (POST with JSON)
- Images: `http://YOUR_PC_IP:5019/clip` (POST multipart upload)

Replace `YOUR_PC_IP` with your actual PC's IP address on the local network.
