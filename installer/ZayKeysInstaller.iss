#define MyAppName "ZAY KEYS"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "GOLDMINE AUDIO"

[Setup]
AppId={{A71E5C9D-9C14-4A7A-9B51-2E2F3C5D7A10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={commoncf}\VST3
DefaultGroupName=ZAY KEYS
DisableProgramGroupPage=yes
DisableDirPage=no
UsePreviousAppDir=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
OutputDir=..\output
OutputBaseFilename=ZAY_KEYS_Installer_v1.0.1_Windows
SetupIconFile=..\assets\generated\zaykeys.ico
WizardImageFile=..\assets\generated\wizard_side.bmp
WizardSmallImageFile=..\assets\generated\wizard_small.bmp
WizardStyle=modern
WizardSizePercent=100
UninstallDisplayName=ZAY KEYS VST3
Uninstallable=yes
Compression=lzma2/ultra64
SolidCompression=yes
MinVersion=10.0
VersionInfoVersion=1.0.1.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=ZAY KEYS VST3 Instrument Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
CloseApplications=no
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Types]
Name: "full"; Description: "Full installation"
Name: "compact"; Description: "Plugin only"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "vst3"; Description: "ZAY KEYS VST3 instrument (required)"; Types: full compact custom; Flags: fixed
Name: "docs"; Description: "Documentation and FL Studio setup guide"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut to the installation folder"; GroupDescription: "Additional options:"; Flags: unchecked

[Dirs]
Name: "{userdocs}\GOLDMINE AUDIO\ZAY KEYS\Documentation"; Components: docs

[Files]
Source: "..\payload\ZAY KEYS.vst3\*"; DestDir: "{app}\ZAY KEYS.vst3"; Components: vst3; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\payload\Documentation\*"; DestDir: "{userdocs}\GOLDMINE AUDIO\ZAY KEYS\Documentation"; Components: docs; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ZAY KEYS Documentation"; Filename: "{userdocs}\GOLDMINE AUDIO\ZAY KEYS\Documentation\README.md"; Components: docs
Name: "{group}\Uninstall ZAY KEYS"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ZAY KEYS VST3 Folder"; Filename: "{app}"; Tasks: desktopicon

[Code]
function InitializeSetup(): Boolean;
begin
  if not IsWin64 then
  begin
    MsgBox('ZAY KEYS requires 64-bit Windows 10 or Windows 11.', mbCriticalError, MB_OK);
    Result := False;
    exit;
  end;
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    Log('ZAY KEYS VST3 installation completed. Destination: ' + ExpandConstant('{app}\ZAY KEYS.vst3'));
end;
