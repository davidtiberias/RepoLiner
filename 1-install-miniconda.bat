@echo off
cls

:: =================================================================
:: RepoLiner Setup - Step 1: Install Miniconda
:: =================================================================
:: This script will automatically:
:: 1. Check if Miniconda is already installed.
:: 2. Download the latest Miniconda (64-bit) installer for Windows.
:: 3. Install it silently for the current user (no admin rights needed).
:: =================================================================
echo.
echo RepoLiner Setup - Step 1 of 2: Installing Miniconda
echo ----------------------------------------------------
echo.

:: --- Check if Miniconda is already installed ---
if exist "%UserProfile%\miniconda3\Scripts\activate.bat" (
    echo Miniconda appears to be already installed at:
    echo "%UserProfile%\miniconda3"
    echo.
    echo Skipping installation. Please proceed to Step 2.
    echo.
    pause
    goto :eof
)

:: --- Configuration ---
set "MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "INSTALLER_NAME=Miniconda-Installer.exe"

:: --- Download Miniconda using PowerShell ---
echo Downloading Miniconda installer...
powershell -Command "Invoke-WebRequest -Uri %MINICONDA_URL% -OutFile %INSTALLER_NAME%"

if not exist "%INSTALLER_NAME%" (
    echo ERROR: Failed to download the Miniconda installer.
    echo Please check your internet connection and try again.
    pause
    goto :eof
)

echo Download complete.
echo.

:: --- Install Miniconda silently ---
echo Installing Miniconda silently. This may take a few minutes...
:: /S           = Silent mode
:: /InstallationType=JustMe = No admin rights required, installs to user profile
:: /AddToPath=0   = Recommended for stability
:: /RegisterPython=0 = Does not make this the system's default Python
start /wait "" %INSTALLER_NAME% /S /InstallationType=JustMe /AddToPath=0 /RegisterPython=0

:: --- Cleanup ---
echo Cleaning up installer file...
del %INSTALLER_NAME%
echo.

echo ===================================================
echo   SUCCESS: Miniconda has been installed.
echo ===================================================
echo.
echo Please close this window and run the next script:
echo   2-create-environment.bat
echo.
pause