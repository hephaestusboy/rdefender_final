; RDefender Windows Installer Script
; Built with NSIS (Nullsoft Scriptable Install System)

!include "MUI2.nsh"
!include "x64.nsh"

; General
Name "RDefender"
OutFile "RDefender-Setup.exe"
InstallDir "$PROGRAMFILES\RDefender"
InstallDirRegKey HKLM "Software\RDefender" "Install_Dir"
RequestExecutionLevel admin

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy all files from the dist\RDefender folder
    File /r "dist\RDefender\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Create registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RDefender" "DisplayName" "RDefender"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RDefender" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RDefender" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RDefender" "DisplayVersion" "3.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RDefender" "Publisher" "RDefender Team"
    
    ; Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\RDefender"
    CreateShortcut "$SMPROGRAMS\RDefender\RDefender.lnk" "$INSTDIR\RDefender.exe"
    CreateShortcut "$SMPROGRAMS\RDefender\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Create desktop shortcut
    CreateShortcut "$DESKTOP\RDefender.lnk" "$INSTDIR\RDefender.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove start menu
    RMDir /r "$SMPROGRAMS\RDefender"
    
    ; Remove desktop shortcut
    Delete "$DESKTOP\RDefender.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RDefender"
    DeleteRegKey HKLM "Software\RDefender"
SectionEnd
