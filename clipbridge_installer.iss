[Setup]
AppId={{E8F9A2D4-3B5C-4F7E-9A1D-6E8C5B4A7F3E}
AppName=Clipbridge
AppVersion=1.0.0
AppPublisher=Blake
AppPublisherURL=https://github.com/blake/clipbridge
AppSupportURL=https://github.com/blake/clipbridge
AppUpdatesURL=https://github.com/blake/clipbridge
DefaultDirName={autopf}\Clipbridge
DefaultGroupName=Clipbridge
AllowNoIcons=yes
LicenseFile=
PrivilegesRequired=admin
OutputDir=dist
OutputBaseFilename=Clipbridge-Setup
SetupIconFile=ic_fluent_clipboard_20_color.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Main application files
Source: "clipbridge.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "ic_fluent_clipboard_20_color.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "SERVICE_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion

; NSSM for service management
Source: "nssm\nssm.exe"; DestDir: "{app}\nssm"; Flags: ignoreversion

; Python installer (embed Python)
Source: "python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs

; Installation scripts
Source: "setup_service.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall_service.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Clipbridge"; Filename: "{app}\python\python.exe"; Parameters: "{app}\clipbridge.py"; WorkingDir: "{app}"; IconFilename: "{app}\ic_fluent_clipboard_20_color.ico"
Name: "{group}\Start Clipbridge Service"; Filename: "{app}\setup_service.bat"; WorkingDir: "{app}"; IconFilename: "{app}\ic_fluent_clipboard_20_color.ico"
Name: "{group}\Stop Clipbridge Service"; Filename: "{app}\uninstall_service.bat"; WorkingDir: "{app}"; IconFilename: "{app}\ic_fluent_clipboard_20_color.ico"
Name: "{group}\{cm:UninstallProg,Clipbridge}"; Filename: "{uninstallexe}"

[Run]
; Install Python dependencies
Filename: "{app}\python\python.exe"; Parameters: "-m pip install --upgrade pip"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated; StatusMsg: "Updating pip..."
Filename: "{app}\python\python.exe"; Parameters: "-m pip install -r requirements.txt"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated; StatusMsg: "Installing Python dependencies..."

; Install and start the service
Filename: "{app}\setup_service.bat"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated; StatusMsg: "Installing Clipbridge service..."

; Open firewall port
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""Clipbridge"" dir=in action=allow protocol=TCP localport=5019"; Flags: runhidden waituntilterminated; StatusMsg: "Configuring Windows Firewall..."

[UninstallRun]
; Stop and remove the service
Filename: "{app}\uninstall_service.bat"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated

; Remove firewall rule
Filename: "netsh"; Parameters: "advfirewall firewall delete rule name=""Clipbridge"""; Flags: runhidden

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if Python is available
  if not FileExists(ExpandConstant('{app}\python\python.exe')) then
  begin
    // We'll embed Python, so this check might not be needed
    // but keeping it for safety
  end;
end;
