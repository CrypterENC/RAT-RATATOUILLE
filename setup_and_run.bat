@echo off
title RAT Environment Setup and Launch
color 0A

echo ===================================================
echo  RATATOUILLE - Environment Setup and Launch Script
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo [INFO] Setting up virtual environment...
echo.

:: Run the virtual environment creation script
python create_venv.py

if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo.
echo [INFO] Virtual environment created successfully.

:: Install requirements automatically
echo [INFO] Installing requirements...
call venv_folder\.venv\Scripts\activate.bat

:: Update pip to latest version
echo [INFO] Updating pip to latest version...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to update pip, continuing with installation...
) else (
    echo [INFO] Pip updated successfully.
)

pip install -r requirements.txt
echo [INFO] Requirements installed successfully.

:: Prompt user before launching server
echo.
echo ===================================================
echo  IMPORTANT: The RAT server will now be launched in 
echo  a new window. Please do not close this window 
echo  until you're done with the server.
echo ===================================================
echo.
pause

:: Launch the server in a new window
echo [INFO] Launching RAT server in the virtual environment...
start cmd /k "venv_folder\.venv\Scripts\activate.bat && python rat_server.py && exit"

echo.
echo ===================================================
echo  Setup complete! The server is now running in a 
echo  separate window.
echo ===================================================
echo.
echo This window will close in 5 seconds...

:: Wait a moment and then close this window
timeout /t 5 >nul
exit



