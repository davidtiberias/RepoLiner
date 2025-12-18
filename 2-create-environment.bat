@echo off
cls

:: =================================================================
:: RepoLiner Setup - Step 2: Create Conda Environment
:: =================================================================
:: This script will automatically:
:: 1. Locate your new Miniconda installation.
:: 2. Create the dedicated 'repoliner-env' Conda environment.
:: =================================================================
echo.
echo RepoLiner Setup - Step 2 of 2: Creating Environment
echo ----------------------------------------------------
echo.

:: --- Configuration ---
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"

:: --- Check if Miniconda was installed first ---
if not exist "%CONDA_PATH%" (
    echo ERROR: Miniconda installation not found.
    echo Please run '1-install-miniconda.bat' successfully before running this script.
    pause
    goto :eof
)

:: --- Activate the base environment to get access to the 'conda' command ---
echo Locating Conda and setting up environment...
call "%CONDA_PATH%"

:: --- Create the environment from the file ---
echo Creating the 'repoliner-env'. This will download required packages...
conda env create -f environment.yml

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create the Conda environment.
    echo Please check the error messages above.
    pause
    goto :eof
)

echo.
echo ===================================================
echo   SUCCESS: The RepoLiner environment is ready!
echo ===================================================
echo.
echo Setup is now complete. You can now run 'launch.bat'
echo to start using the program.
echo.
pause