@echo off
cls

:: =================================================================
:: RepoLiner Setup - Step 3: Install Python Dependencies
:: =================================================================
:: This script will automatically:
:: 1. Activate the 'repoliner-env' Conda environment.
:: 2. Install all required Python packages using pip and requirements.txt.
:: =================================================================
echo.
echo RepoLiner Setup - Step 3 of 3: Installing Python Dependencies
echo ---------------------------------------------------------------
echo.

:: --- Configuration ---
set "CONDA_ENV_NAME=repoliner-env"
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"

:: --- Check if environment exists (by checking if step 2 was likely run) ---
if not exist "%UserProfile%\miniconda3\envs\%CONDA_ENV_NAME%" (
    echo ERROR: The '%CONDA_ENV_NAME%' environment was not found.
    echo Please run '2-create-environment.bat' successfully before this script.
    pause
    goto :eof
)

:: --- Activate the Conda Environment ---
echo Activating the '%CONDA_ENV_NAME%' environment...
call "%CONDA_PATH%"
call conda activate %CONDA_ENV_NAME%

if errorlevel 1 (
    echo ERROR: Failed to activate the Conda environment.
    pause
    goto :eof
)

:: --- Install packages from requirements.txt ---
echo Installing packages from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install packages using pip.
    echo Please check the error messages above.
    pause
    goto :eof
)

echo.
echo ===================================================================
echo   SUCCESS: All Python dependencies have been installed.
echo ===================================================================
echo.
echo Setup is now fully complete. You can run 'launch.bat' to use the tool.
echo.
pause