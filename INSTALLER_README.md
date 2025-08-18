# Clipbridge Installer

This creates a Windows installer for Clipbridge that makes it super easy to deploy on any computer.

## What the Installer Does

✅ **Embeds Python** - No need to install Python separately  
✅ **Installs Dependencies** - Automatically installs all required packages  
✅ **Creates Windows Service** - Runs automatically at startup  
✅ **Configures Firewall** - Opens port 5019 for iPhone access  
✅ **Easy Uninstall** - Complete removal including service  

## Building the Installer

### Step 1: Prepare Build Files
```powershell
# Run the build preparation script
.\build_installer.ps1
```

This will:
- Download NSSM (service manager)
- Download Python embeddable package
- Prepare all necessary files

### Step 2: Install Inno Setup
1. Download Inno Setup from: https://jrsoftware.org/isinfo.php
2. Install it on your computer

### Step 3: Compile Installer
1. Open `clipbridge_installer.iss` in Inno Setup Compiler
2. Click "Compile" (or press F9)
3. The installer will be created in the `dist` folder

## What Gets Installed

The installer creates this structure:
```
C:\Program Files\Clipbridge\
├── clipbridge.py          # Main application
├── requirements.txt       # Python dependencies
├── ic_fluent_clipboard_20_color.ico
├── python\               # Embedded Python runtime
│   ├── python.exe
│   └── ... (Python files)
├── nssm\                 # Service manager
│   └── nssm.exe
├── logs\                 # Service logs
├── setup_service.bat     # Service installer
└── uninstall_service.bat # Service remover
```

## After Installation

1. **Service runs automatically** - Clipbridge starts with Windows
2. **Find your PC's IP** - Run `ipconfig` in Command Prompt
3. **Configure iPhone shortcuts** with `http://YOUR_PC_IP:5019/clip`

## Service Management

The installer creates Start Menu shortcuts for:
- **Start Clipbridge Service** - Manually start the service
- **Stop Clipbridge Service** - Stop the service
- **Uninstall** - Complete removal

## Manual Service Commands

```batch
# Check service status
sc query Clipbridge

# Start service manually
net start Clipbridge

# Stop service
net stop Clipbridge
```

## Firewall

The installer automatically:
- Opens port 5019 in Windows Firewall
- Removes the rule during uninstall

## Logs

Service logs are saved to:
- `C:\Program Files\Clipbridge\logs\clipbridge.log`
- `C:\Program Files\Clipbridge\logs\clipbridge_error.log`

## iPhone Setup

After installation, configure your iPhone shortcuts:

### Text Shortcut
- URL: `http://YOUR_PC_IP:5019/clip`
- Method: POST
- Body: JSON with `{"text": "clipboard content"}`

### Image Shortcut  
- URL: `http://YOUR_PC_IP:5019/clip`
- Method: POST
- Body: Upload image as multipart/form-data

## Troubleshooting

1. **Service won't start**: Check logs in `C:\Program Files\Clipbridge\logs\`
2. **iPhone can't connect**: Verify Windows Firewall and network connectivity
3. **Permission issues**: Run as Administrator

## Uninstalling

Use the Windows "Add or Remove Programs" feature, or run the uninstaller from the Start Menu. This will:
- Stop the service
- Remove the service
- Remove firewall rules
- Delete all program files
