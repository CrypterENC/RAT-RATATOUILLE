@echo off
setlocal enabledelayedexpansion
title Ratatouille Environment Setup


:: Error handling
setlocal enableextensions

:: Enable ANSI escape sequences for colors
for /f "tokens=4-5 delims=. " %%i in ('ver') do set "version=%%i.%%j"
if "%version%" == "10.0" (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
)

:: Define ANSI color codes with proper escape character
set "ESC="
for /f %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
set "RESET=%ESC%[0m"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "MAGENTA=%ESC%[95m"
set "CYAN=%ESC%[96m"
set "WHITE=%ESC%[97m"
set "BOLD=%ESC%[1m"

:: Define additional ANSI color codes for the gradient
set "LIGHTRED=%ESC%[91m"
set "LIGHTBLUE=%ESC%[94m"
set "BLUE=%ESC%[34m"

:: Display welcome message with gradient colors (RED -> LIGHTRED -> WHITE -> LIGHTBLUE -> BLUE)
echo %RED%=======%LIGHTRED%=======%WHITE%=======%LIGHTBLUE%=======%BLUE%=======%RESET%
echo %RED%W%RED%E%LIGHTRED%L%LIGHTRED%C%WHITE%O%WHITE%M%WHITE%E %LIGHTRED%T%LIGHTRED%O %RED%R%RED%A%LIGHTRED%T%LIGHTRED%A%WHITE%T%WHITE%O%LIGHTBLUE%U%LIGHTBLUE%I%BLUE%L%BLUE%L%BLUE%E%RESET%
echo %RED%=======%LIGHTRED%=======%WHITE%=======%LIGHTBLUE%=======%BLUE%=======%RESET%

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo %ESC%%RED%%BOLD%[!] This script requires administrator privileges.%ESC%%RESET%
    echo %ESC%%RED%%BOLD%[!] Please right-click and select "Run as administrator".%ESC%%RESET%
    echo.
    pause
    exit /b 1
)

:: Create temp directory
set "TEMP_DIR=%TEMP%\dev_setup_%RANDOM%"
set "DESKTOP_PATH=%USERPROFILE%\Desktop"
set "LOG_FILE=%TEMP_DIR%\setup_log.txt"
mkdir "%TEMP_DIR%" 2>nul

echo %ESC%%CYAN%%BOLD%[*] Setting up development environment...%ESC%%RESET%
echo %ESC%%CYAN%[*] Temporary directory: %TEMP_DIR%%ESC%%RESET%

:: Check internet connection
echo %ESC%%CYAN%%BOLD%[*] Checking internet connection...%ESC%%RESET%
ping -n 1 www.google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%%RED%%BOLD%[!] No internet connection detected.%ESC%%RESET%
    goto :cleanup
)
echo %ESC%%GREEN%%BOLD%[+] Internet connection verified.%ESC%%RESET%

:: Download Python 3.12.9 directly
echo %ESC%%CYAN%[*] Downloading Python 3.12.9...%ESC%%RESET%
set "PYTHON_VERSION=3.12.9"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
set "PYTHON_INSTALLER=%TEMP_DIR%\python_installer.exe"

powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_INSTALLER%')"
if %errorlevel% neq 0 (
    echo %ESC%%RED%%BOLD%[!] Error downloading Python installer.%ESC%%RESET%
    goto :cleanup
)
echo %ESC%%GREEN%[+] Python download complete!%ESC%%RESET%

:: Copy Python installer to desktop
copy "%PYTHON_INSTALLER%" "%DESKTOP_PATH%\python_installer.exe" >nul
echo %ESC%%GREEN%[+] Copied installer to desktop: %DESKTOP_PATH%\python_installer.exe%ESC%%RESET%

:: Install Python automatically
echo %ESC%%CYAN%[*] Installing Python 3.12.9 (this may take a few minutes)...%ESC%%RESET%
start /wait "" "%PYTHON_INSTALLER%" /passive InstallAllUsers=1 PrependPath=1 Include_test=0
echo %ESC%%GREEN%[+] Python installation complete!%ESC%%RESET%

:: Ensure Python is in PATH
echo %ESC%%CYAN%[*] Adding Python to PATH...%ESC%%RESET%
setx PATH "%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts" /M
echo %ESC%%GREEN%[+] Python added to PATH.%ESC%%RESET%

:: Upgrade pip, setuptools and install virtualenv
echo %ESC%%CYAN%[*] Upgrading pip, setuptools and installing virtualenv...%ESC%%RESET%
py -m pip install --upgrade pip setuptools virtualenv
if %errorlevel% neq 0 (
    echo %ESC%%YELLOW%[!] Warning: Could not upgrade pip and setuptools. Will try again later.%ESC%%RESET%
) else (
    echo %ESC%%GREEN%[+] Successfully upgraded pip, setuptools and installed virtualenv.%ESC%%RESET%
)

:: Download MSYS2
echo %ESC%%CYAN%[*] Downloading MSYS2...%ESC%%RESET%
set "MSYS2_URL=https://github.com/msys2/msys2-installer/releases/download/2023-07-18/msys2-x86_64-20230718.exe"
set "MSYS2_INSTALLER=%TEMP_DIR%\msys2_installer.exe"

powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%MSYS2_URL%', '%MSYS2_INSTALLER%')"
echo %ESC%%GREEN%[+] MSYS2 download complete!%ESC%%RESET%

:: Copy MSYS2 installer to desktop
copy "%MSYS2_INSTALLER%" "%DESKTOP_PATH%\msys2_installer.exe" >nul
echo %ESC%%GREEN%[+] Copied installer to desktop: %DESKTOP_PATH%\msys2_installer.exe%ESC%%RESET%

:: Install MSYS2 automatically
echo %ESC%%CYAN%[*] Installing MSYS2 (this may take a few minutes)...%ESC%%RESET%
start /wait "" "%MSYS2_INSTALLER%" --confirm-command --accept-messages --root C:/msys64
echo %ESC%%GREEN%[+] MSYS2 installation complete!%ESC%%RESET%

:: Update MSYS2 packages
echo %ESC%%CYAN%[*] Updating MSYS2 packages...%ESC%%RESET%
set "MSYS2_SHELL=C:\msys64\usr\bin\bash.exe"

echo %ESC%%CYAN%[*] Running first update (this may take a few minutes)...%ESC%%RESET%
"%MSYS2_SHELL%" -l -c "pacman -Syu --noconfirm"

echo %ESC%%CYAN%[*] Installing development tools (this may take a few minutes)...%ESC%%RESET%
"%MSYS2_SHELL%" -l -c "pacman -S --noconfirm mingw-w64-x86_64-toolchain mingw-w64-x86_64-cmake make"

:: Add MSYS2 to PATH
echo %ESC%%CYAN%[*] Adding MSYS2 to PATH...%ESC%%RESET%
setx PATH "%PATH%;C:\msys64\mingw64\bin" /M
echo %ESC%%GREEN%[+] MSYS2 added to PATH.%ESC%%RESET%

:: Install Python packages
echo %ESC%%CYAN%[*] Installing Python packages...%ESC%%RESET%
py -m pip install --upgrade pip setuptools virtualenv
py -m pip install pyinstaller cx_Freeze py2exe colorama requests
echo %ESC%%GREEN%[+] Python packages installed.%ESC%%RESET%

:: Verify installations
echo %ESC%%CYAN%%BOLD%[*] Verifying installations...%ESC%%RESET%

:: Verify Python installation
echo %ESC%%CYAN%[*] Checking Python installation...%ESC%%RESET%
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%%RED%[!] Python verification failed. Please check installation.%ESC%%RESET%
) else (
    for /f "tokens=*" %%i in ('py --version') do set PYTHON_VERSION=%%i
    echo %ESC%%GREEN%[+] %PYTHON_VERSION% successfully installed.%ESC%%RESET%
)

:: Verify MSYS2/MinGW installation
echo %ESC%%CYAN%[*] Checking MinGW installation...%ESC%%RESET%
g++ --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%%RED%[!] MinGW (g++) verification failed. Please check installation.%ESC%%RESET%
    echo %ESC%%YELLOW%[!] You may need to restart your computer for PATH changes to take effect.%ESC%%RESET%
) else (
    for /f "tokens=*" %%i in ('g++ --version 2^>^&1 ^| findstr /R /C:"^g++"') do set GCC_VERSION=%%i
    echo %ESC%%GREEN%[+] MinGW (%GCC_VERSION%) successfully installed.%ESC%%RESET%
)

:: Remind user to disable Python App Execution Aliases
echo.
echo %ESC%%RED%%BOLD%===============================================================%ESC%%RESET%
echo %ESC%%RED%%BOLD%[!] CRITICAL POST-INSTALLATION STEP - MUST COMPLETE%ESC%%RESET%
echo %ESC%%RED%%BOLD%===============================================================%ESC%%RESET%
echo %ESC%%YELLOW%%BOLD%[!] Disable Python App Execution Aliases:%ESC%%RESET%
echo %ESC%%YELLOW%[!] 1. Open Windows Settings (Win+I)%ESC%%RESET%
echo %ESC%%YELLOW%[!] 2. Search for "Manage App Execution Aliases"%ESC%%RESET%
echo %ESC%%YELLOW%[!] 3. Turn OFF App Installer for both python.exe and python3.exe%ESC%%RESET%
echo %ESC%%RED%%BOLD%===============================================================%ESC%%RESET%
echo.

echo %ESC%%GREEN%%BOLD%[+] Setup complete!%ESC%%RESET%
echo %ESC%%YELLOW%[!] Please restart your computer to ensure all changes take effect.%ESC%%RESET%
echo.

:: Add countdown timer before closing
echo %ESC%%CYAN%[*] This window will close in 10 seconds...%ESC%%RESET%
for /l %%i in (10,-1,1) do (
    echo %ESC%%CYAN%[*] Closing in %%i seconds...%ESC%%RESET%
    timeout /t 1 /nobreak >nul
)

:: Exit the script
exit

