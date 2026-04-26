@echo off
cls

:: =================================================================
:: RepoLiner Setup - Step 2: Create Environment & Install Dependencies
:: =================================================================
:: This script will automatically:
:: 1. Locate your Miniconda installation.
:: 2. Create the 'repoliner-env' Conda environment from environment.yml.
:: 3. Install all Python packages specified in the file.
:: =================================================================
echo.
echo RepoLiner Setup - Step 2 of 2: Creating Environment & Installing Dependencies
echo --------------------------------------------------------------------------
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
echo Creating 'repoliner-env' and installing all packages. This may take a while...
conda env create -f environment.yml --force

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create the Conda environment.
    echo Please check the error messages above.
    pause
    goto :eof
)

echo.
echo ===================================================================
echo   SUCCESS: The RepoLiner environment and all dependencies are ready!
echo ===================================================================
echo.
echo Setup is complete. You can now run 'launch.bat' to start the program.
echo.
pause
