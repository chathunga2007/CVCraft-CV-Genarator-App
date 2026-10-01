; =====================================================================
; CVCraft Professional Resume & CV Workstation
; Inno Setup 6 / 7 Installer Script
; Lead Architect & Developer: Chathunga Bimsara
; Repository: https://github.com/chathunga2007/CVCraft-CV-Genarator-App
; =====================================================================

#define MyAppName "CVCraft"
#define MyAppVersion "v1.0.0"
#define MyAppPublisher "Chathunga Bimsara"
#define MyAppURL "https://github.com/chathunga2007/CVCraft-CV-Genarator-App"
#define MyAppExeName "CVCraft.exe"
#define MyAppAssocName MyAppName + " Career Document"
#define MyAppAssocExt ".cvcv"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt
#define MyAppAppUserModelID "CVCraft.ProfessionalResumeBuilder.App.1.0"

[Setup]
; App Identity
AppId={{8B1A249D-F138-4F12-87BC-3B3674683072}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; Default Installation Directory
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
ChangesAssociations=yes

; Visuals & Wizard Style
WizardStyle=modern
WizardResizable=yes
WizardSizePercent=105,105
SetupIconFile=assets\cvcraft.ico
LicenseFile=LICENSE

; Compression & Output Architecture
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=CVCraft_Setup_v1.0.0

; Privileges: allows both per-user or administrative install
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon"; Description: "Create a Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Standalone compiled distribution package
Source: "dist\CVCraft\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Root assets and branding resources
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; Default template database and configurations
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation & License
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Main Shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\cvcraft.ico"; AppUserModelID: "{#MyAppAppUserModelID}"; Tasks: startmenuicon
; Start Menu Uninstaller Shortcut
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop Shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\cvcraft.ico"; AppUserModelID: "{#MyAppAppUserModelID}"; Tasks: desktopicon

[Registry]
; Register .cvcv File Association
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\assets\cvcraft.ico,0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

; Register Windows Taskbar & Shell AppUserModelID
Root: HKCU; Subkey: "Software\Classes\AppUserModelId\{#MyAppAppUserModelID}"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName} — Professional Resume Builder"
Root: HKCU; Subkey: "Software\Classes\AppUserModelId\{#MyAppAppUserModelID}"; ValueType: string; ValueName: "IconUri"; ValueData: "{app}\assets\cvcraft.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
