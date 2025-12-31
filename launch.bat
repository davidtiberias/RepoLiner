@echo off
cls

:: =================================================================
:: RepoLiner - Main Launcher
:: =================================================================
:: This script can be run in two ways:
:: 1. Double-click it: It will ask you to enter a project directory.
:: 2. From CMD:      Pass a directory path as an argument, e.g.,
::                   launch.bat "D:\My Project"
:: =================================================================

:: --- Configuration ---
set "CONDA_ENV_NAME=repoliner-env"
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"
set "SCRIPT_PATH=%~dp0scripts\merge_script.py"

:: --- Check if a directory was passed as an argument ---
set "TARGET_DIR=%~1"

:: If no argument is provided, prompt the user for input
if "%TARGET_DIR%"=="" (
    echo RepoLiner - Project Code Consolidator
    echo --------------------------------------------------
    echo.
    set /p "TARGET_DIR=Please enter the full path to the project directory to scan: "
    echo.
)

:: --- Validate Input ---
if "%TARGET_DIR%"=="" (
    echo ERROR: No directory provided. Exiting.
    pause
    goto :eof
)
if not exist "%TARGET_DIR%" (
    echo ERROR: The specified directory does not exist:
    echo "%TARGET_DIR%"
    pause
    goto :eof
)

:: --- Activate Conda Environment (silently) ---
echo Activating Conda environment '%CONDA_ENV_NAME%'...
call "%CONDA_PATH%" > nul 2>&1
call conda activate %CONDA_ENV_NAME% > nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Failed to activate Conda environment '%CONDA_ENV_NAME%'.
    echo Please ensure it was created with 'conda env create -f environment.yml'.
    echo.
    pause
    goto :eof
)

:: --- Run the Python Script ---
:: Pass the final target directory to the Python script.
echo Running RepoLiner on "%TARGET_DIR%"...
echo --------------------------------------------------
python "%SCRIPT_PATH%" "%TARGET_DIR%"
echo.

echo ==================================================
echo   RepoLiner has finished.
echo   Check the 'output' folder for the result.
echo ==================================================
echo.
pause