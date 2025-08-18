# Clipbridge Installer Build Script
# This script helps prepare all files needed for the Inno Setup installer

param(
    [string]$OutputDir = "installer_build"
)

Write-Host "Preparing Clipbridge Installer Build..." -ForegroundColor Green

# Create output directory
if (Test-Path $OutputDir) {
    Remove-Item $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir | Out-Null

Write-Host "Created build directory: $OutputDir" -ForegroundColor Yellow

# Copy main application files
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item "clipbridge.py" "$OutputDir\"
Copy-Item "requirements.txt" "$OutputDir\"
Copy-Item "ic_fluent_clipboard_20_color.ico" "$OutputDir\"
Copy-Item "SERVICE_SETUP.md" "$OutputDir\"
Copy-Item "setup_service.bat" "$OutputDir\"
Copy-Item "uninstall_service.bat" "$OutputDir\"
Copy-Item "clipbridge_installer.iss" "$OutputDir\"

# Download NSSM if not present
$nssmDir = "$OutputDir\nssm"
New-Item -ItemType Directory -Path $nssmDir -Force | Out-Null

if (-not (Test-Path "$nssmDir\nssm.exe")) {
    Write-Host "Downloading NSSM..." -ForegroundColor Yellow
    
    $nssmUrl = "https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip"
    $nssmZip = "$OutputDir\nssm.zip"
    
    try {
        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
        
        # Extract NSSM
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($nssmZip, "$OutputDir\nssm_temp")
        
        # Copy the 64-bit version
        $nssmExe = Get-ChildItem "$OutputDir\nssm_temp" -Recurse -Name "nssm.exe" | Where-Object { $_ -like "*win64*" } | Select-Object -First 1
        if ($nssmExe) {
            Copy-Item "$OutputDir\nssm_temp\$nssmExe" "$nssmDir\nssm.exe"
            Write-Host "NSSM downloaded and extracted successfully!" -ForegroundColor Green
        } else {
            Write-Host "Could not find NSSM executable in download" -ForegroundColor Red
        }
        
        # Clean up
        Remove-Item $nssmZip -Force
        Remove-Item "$OutputDir\nssm_temp" -Recurse -Force
        
    } catch {
        Write-Host "Failed to download NSSM automatically. Please download manually from https://nssm.cc/download" -ForegroundColor Red
        Write-Host "Extract nssm.exe (64-bit version) to: $nssmDir\nssm.exe" -ForegroundColor Yellow
    }
} else {
    Write-Host "NSSM already present" -ForegroundColor Green
}

# Download Python embeddable package
$pythonDir = "$OutputDir\python"
New-Item -ItemType Directory -Path $pythonDir -Force | Out-Null

if (-not (Test-Path "$pythonDir\python.exe")) {
    Write-Host "Downloading Python embeddable package..." -ForegroundColor Yellow
    
    $pythonVersion = "3.11.9"
    $pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-embed-amd64.zip"
    $pythonZip = "$OutputDir\python.zip"
    
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
        
        # Extract Python
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($pythonZip, $pythonDir)
        
        # Enable site-packages by modifying python311._pth
        $pthFile = Get-ChildItem $pythonDir -Name "python*._pth" | Select-Object -First 1
        if ($pthFile) {
            $pthPath = "$pythonDir\$pthFile"
            $pthContent = Get-Content $pthPath
            $pthContent = $pthContent -replace "#import site", "import site"
            $pthContent | Set-Content $pthPath
            Write-Host "Enabled site-packages in Python" -ForegroundColor Green
        }
        
        # Download get-pip.py
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$pythonDir\get-pip.py"
        
        # Install pip
        Write-Host "Installing pip..." -ForegroundColor Yellow
        & "$pythonDir\python.exe" "$pythonDir\get-pip.py" --quiet
        
        Write-Host "Python embeddable package downloaded and configured successfully!" -ForegroundColor Green
        
        # Clean up
        Remove-Item $pythonZip -Force
        Remove-Item "$pythonDir\get-pip.py" -Force
        
    } catch {
        Write-Host "Failed to download Python automatically. Please download manually:" -ForegroundColor Red
        Write-Host "1. Download Python $pythonVersion embeddable package from python.org" -ForegroundColor Yellow
        Write-Host "2. Extract to: $pythonDir" -ForegroundColor Yellow
        Write-Host "3. Install pip in the embeddable Python" -ForegroundColor Yellow
    }
} else {
    Write-Host "Python already present" -ForegroundColor Green
}

Write-Host ""
Write-Host "Build preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install Inno Setup from: https://jrsoftware.org/isinfo.php" -ForegroundColor White
Write-Host "2. Open clipbridge_installer.iss in Inno Setup" -ForegroundColor White
Write-Host "3. Compile to create the installer" -ForegroundColor White
Write-Host ""
Write-Host "Build directory contents:" -ForegroundColor Yellow
Get-ChildItem $OutputDir -Recurse | Format-Table Name, Length, LastWriteTime
