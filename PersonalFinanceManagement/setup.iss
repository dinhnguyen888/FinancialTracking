[Setup]
AppName=Personal Finance Management
AppVersion=1.0
DefaultDirName={localappdata}\PersonalFinanceManagement
DefaultGroupName=Personal Finance Management
OutputDir=Output
OutputBaseFilename=Setup_PersonalFinance
SetupIconFile=Icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "bin\Release\net8.0-windows\win-x64\publish\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Personal Finance Management"; Filename: "{app}\PersonalFinanceManagement.exe"
Name: "{commondesktop}\Personal Finance Management"; Filename: "{app}\PersonalFinanceManagement.exe"

[Run]
Filename: "{app}\PersonalFinanceManagement.exe"; Description: "Khởi động ứng dụng"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
