; Inno Setup Script for Antidetect Browser
; Requires Inno Setup 6.x: https://jrsoftware.org/isinfo.php

#define MyAppName "Antidetect Browser"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Antidetect Team"
#define MyAppURL "https://github.com/antidetect/antidetect-playwright"
#define MyAppExeName "AntidetectBrowser.exe"
#define MyAppId "{{8F9A5B2C-3D4E-5F6A-7B8C-9D0E1F2A3B4C}"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\README.md
; Uncomment the following line to run in non administrative install mode (install for current user only.)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=AntidetectBrowser-Setup-{#MyAppVersion}
SetupIconFile=icons\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
; Require Windows 10 or later
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files
Source: "..\dist\AntidetectBrowser\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up app data on uninstall
Type: filesandordirs; Name: "{localappdata}\AntidetectBrowser"
Type: filesandordirs; Name: "{userappdata}\AntidetectBrowser"

[Code]
// Custom installation logic

var
  UpdateCheckPage: TInputOptionWizardPage;
  AutoUpdateEnabled: Boolean;

procedure InitializeWizard;
begin
  // Create auto-update option page
  UpdateCheckPage := CreateInputOptionPage(wpSelectTasks,
    'Auto-Update Settings', 'Configure automatic updates',
    'Select whether you want the application to check for updates automatically.',
    True, False);
  UpdateCheckPage.Add('Enable automatic update checks (recommended)');
  UpdateCheckPage.Values[0] := True;
end;

procedure RegisterPreviousData(PreviousDataKey: Integer);
begin
  // Store auto-update preference
  SetPreviousData(PreviousDataKey, 'AutoUpdate', IntToStr(Integer(UpdateCheckPage.Values[0])));
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
end;

// Check if .NET Framework is installed (if needed)
function IsDotNetInstalled(): Boolean;
begin
  Result := True; // Modify if you need .NET
end;

// Clean installation detection
function IsUpgrade(): Boolean;
var
  Value: string;
begin
  Result := RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1', 'UninstallString', Value) or
            RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1', 'UninstallString', Value);
end;

// Save auto-update setting to registry
procedure CurStepChanged(CurStep: TSetupStep);
var
  AutoUpdateValue: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Save auto-update preference
    if UpdateCheckPage.Values[0] then
      AutoUpdateValue := 1
    else
      AutoUpdateValue := 0;

    if IsAdminInstallMode then
      RegWriteDWordValue(HKLM, 'Software\{#MyAppPublisher}\{#MyAppName}', 'AutoUpdate', AutoUpdateValue)
    else
      RegWriteDWordValue(HKCU, 'Software\{#MyAppPublisher}\{#MyAppName}', 'AutoUpdate', AutoUpdateValue);
  end;
end;

// Uninstall previous version
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  UninstallString: string;
begin
  Result := '';

  if IsUpgrade() then
  begin
    // Get uninstall string
    if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1', 'QuietUninstallString', UninstallString) or
       RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1', 'QuietUninstallString', UninstallString) then
    begin
      // Silently uninstall previous version
      Exec(RemoveQuotes(UninstallString), '', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
