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
korean.ExistingTitle=이미 설치되어 있습니다
english.ExistingTitle=Already installed
korean.ExistingDesc=설치된 버전: %1  →  새 버전: %2
english.ExistingDesc=Installed version: %1  →  new version: %2
korean.ExistingPrompt=어떻게 할까요?
english.ExistingPrompt=What would you like to do?
korean.OptUpdate=업데이트 / 재설치 (설정 유지)
english.OptUpdate=Update / reinstall (keep settings)
korean.OptClean=제거 후 새로 설치 (설정 초기화)
english.OptClean=Uninstall, then install fresh (reset settings)
korean.OptRemove=제거만 하기
english.OptRemove=Uninstall only
korean.UninstallFailed=기존 버전을 제거하지 못했습니다. Windows 설정 → 앱에서 직접 제거한 뒤 다시 실행해 주세요.
english.UninstallFailed=Could not uninstall the existing version. Remove it from Windows Settings → Apps, then run setup again.
korean.Removed=HEIC Converter를 제거했습니다.
english.Removed=HEIC Converter has been uninstalled.

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

[Code]
// Existing install: let the user update, reinstall clean, or just uninstall.
// Silent installs default to update; pass /MODE=clean or /MODE=uninstall to choose.
const
  UninstKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{8C1E5B2A-4F7D-4B8E-9A3C-2D6F1E0B7A54}_is1';
  ModeUpdate = 0;
  ModeClean = 1;
  ModeRemove = 2;

var
  ExistingPage: TInputOptionWizardPage;
  InstalledVersion, UninstallExe: String;
  UninstallOnly: Boolean;

function QueryUninstall(const Name: String; var Value: String): Boolean;
begin
  Result := RegQueryStringValue(HKCU, UninstKey, Name, Value) or
            RegQueryStringValue(HKLM, UninstKey, Name, Value);
end;

function FindExisting(): Boolean;
var
  S: String;
begin
  Result := False;
  if QueryUninstall('UninstallString', S) then
  begin
    UninstallExe := RemoveQuotes(S);
    if not QueryUninstall('DisplayVersion', InstalledVersion) then
      InstalledVersion := '?';
    Result := FileExists(UninstallExe);
  end;
end;

function RunUninstaller(): Boolean;
var
  Code, I: Integer;
begin
  Result := Exec(UninstallExe, '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART', '', SW_HIDE,
                 ewWaitUntilTerminated, Code) and (Code = 0);
  // The uninstaller finishes in a temp copy of itself; wait until it is really gone.
  I := 0;
  while Result and FileExists(UninstallExe) and (I < 120) do
  begin
    Sleep(500);
    I := I + 1;
  end;
  Result := Result and not FileExists(UninstallExe);
end;

function ApplyChoice(Mode: Integer): Boolean;
begin
  Result := True;
  if Mode = ModeUpdate then
    Exit;
  if not RunUninstaller() then
  begin
    SuppressibleMsgBox(CustomMessage('UninstallFailed'), mbError, MB_OK, IDOK);
    Result := False;
    Exit;
  end;
  if Mode = ModeClean then
    DelTree(ExpandConstant('{userappdata}\HEICConverter'), True, True, True)
  else
    UninstallOnly := True;
end;

function InitializeSetup(): Boolean;
var
  Mode: String;
begin
  Result := True;
  if WizardSilent() and FindExisting() then
  begin
    Mode := Lowercase(ExpandConstant('{param:MODE|update}'));
    if Mode = 'clean' then
      Result := ApplyChoice(ModeClean)
    else if Mode = 'uninstall' then
    begin
      ApplyChoice(ModeRemove);
      Result := False;
    end;
  end;
end;

procedure InitializeWizard();
begin
  if (not WizardSilent()) and FindExisting() then
  begin
    ExistingPage := CreateInputOptionPage(wpWelcome, CustomMessage('ExistingTitle'),
      FmtMessage(CustomMessage('ExistingDesc'), [InstalledVersion, '{#AppVersion}']),
      CustomMessage('ExistingPrompt'), True, False);
    ExistingPage.Add(CustomMessage('OptUpdate'));
    ExistingPage.Add(CustomMessage('OptClean'));
    ExistingPage.Add(CustomMessage('OptRemove'));
    ExistingPage.SelectedValueIndex := ModeUpdate;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (ExistingPage <> nil) and (CurPageID = ExistingPage.ID) then
  begin
    Result := ApplyChoice(ExistingPage.SelectedValueIndex);
    if Result and UninstallOnly then
    begin
      MsgBox(CustomMessage('Removed'), mbInformation, MB_OK);
      WizardForm.Close;
      Result := False;
    end;
  end;
end;

procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  if UninstallOnly then
    Confirm := False;
end;
