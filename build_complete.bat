@echo off
REM Complete build script for netmiko-collector
REM This script builds the executable and creates the Windows installer

echo ========================================
echo Complete Build: netmiko-collector
echo ========================================
echo.

REM Step 1: Build executable
call build_installer.bat
if errorlevel 1 (
    echo ERROR: Executable build failed
    exit /b 1
)

echo.
echo ========================================
echo Checking for Inno Setup...
echo ========================================

REM Check if Inno Setup is installed
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_PATH%" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist "%INNO_PATH%" (
    echo.
    echo WARNING: Inno Setup not found!
    echo.
    echo To create a Windows installer, please:
    echo 1. Download Inno Setup from: https://jrsoftware.org/isdl.php
    echo 2. Install it
    echo 3. Run this script again
    echo.
    echo The executable is ready at: dist\netmiko-collector.exe
    echo You can distribute this file manually or install Inno Setup to create an installer.
    echo.
    pause
    exit /b 0
)

echo Inno Setup found at: %INNO_PATH%
echo.
echo Building Windows installer...
"%INNO_PATH%" installer.iss

if errorlevel 1 (
    echo ERROR: Installer build failed
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Files created:
echo   Executable: dist\netmiko-collector.exe
echo   Installer:  installer_output\netmiko-collector-2.0.0-setup.exe
echo.
echo You can now:
echo 1. Run the installer: installer_output\netmiko-collector-2.0.0-setup.exe
echo 2. Distribute the installer to users
echo.

pause
