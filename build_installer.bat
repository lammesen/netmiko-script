@echo off
REM Build script for netmiko-collector Windows installer
REM This script builds the executable and creates an installer

echo ========================================
echo Building netmiko-collector installer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

echo [1/5] Checking dependencies...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo [2/5] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo [3/5] Building executable with PyInstaller...
python -m PyInstaller netmiko-collector.spec --clean

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    exit /b 1
)

echo.
echo [4/5] Verifying executable...
if not exist "dist\netmiko-collector.exe" (
    echo ERROR: Executable not found in dist folder
    exit /b 1
)

echo.
echo [5/5] Testing executable...
"dist\netmiko-collector.exe" --version
if errorlevel 1 (
    echo WARNING: Executable test failed
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\netmiko-collector.exe
echo.
echo To create an installer, you can:
echo 1. Use Inno Setup (recommended) - run: build_inno_setup.bat
echo 2. Manually distribute the dist folder
echo.
echo To test the executable:
echo   cd dist
echo   netmiko-collector.exe --help
echo.

pause
