; Inno Setup 6 script — per-user installer (no admin rights).
; Build: ISCC.exe /DAppVersion=0.5.0 packaging\installer.iss   (after scripts\build.ps1)
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{8C1E5B2A-4F7D-4B8E-9A3C-2D6F1E0B7A54}
AppName=HEIC Converter
AppVersion={#AppVersion}
AppVerName=HEIC Converter {#AppVersion}
AppPublisher=LUDA Research Group
AppCopyright=(c) LUDA Research Group - PolyForm Noncommercial 1.0.0
AppPublisherURL=https://github.com/luda-data-ai-lab/heic-converter
DefaultDirName={autopf}\HEIC Converter
DefaultGroupName=HEIC Converter
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=HEICConverter-Setup-{#AppVersion}
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\HEICConverter.exe
LicenseFile=..\LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
korean.ContextMenu=탐색기 우클릭 메뉴에 "JPG/PNG로 변환" 추가
english.ContextMenu=Add "Convert to JPG/PNG" to the Explorer right-click menu
korean.CliName=HEIC Converter (명령줄)
english.CliName=HEIC Converter (command line)

[Tasks]
Name: "contextmenu"; Description: "{cm:ContextMenu}"
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\HEICConverter.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\HEICConverter-cli.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion
Source: "..\THIRD-PARTY-NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\HEIC Converter"; Filename: "{app}\HEICConverter.exe"
Name: "{autodesktop}\HEIC Converter"; Filename: "{app}\HEICConverter.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\HEICConverter.exe"; Parameters: "--register-shell --lang ko"; Tasks: contextmenu; Languages: korean; Flags: runhidden waituntilterminated
Filename: "{app}\HEICConverter.exe"; Parameters: "--register-shell --lang en"; Tasks: contextmenu; Languages: english; Flags: runhidden waituntilterminated
Filename: "{app}\HEICConverter.exe"; Description: "{cm:LaunchProgram,HEIC Converter}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\HEICConverter.exe"; Parameters: "--unregister-shell"; Flags: runhidden waituntilterminated; RunOnceId: "UnregisterShell"
