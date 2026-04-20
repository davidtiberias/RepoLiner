@echo off
cls

:: =================================================================
:: RepoLiner - Main Launcher (CLI Mode)
:: =================================================================
:: This script can be run in two ways:
:: 1. Double-click it: It will ask you for input interactively.
:: 2. From CMD:      launch.bat "D:\My Project" [folder|dump]
:: =================================================================

:: --- Configuration ---
set "CONDA_ENV_NAME=repoliner-env"
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"
set "SCRIPT_PATH=%~dp0scripts\merge_script.py"

:: --- Check if a directory was passed as an argument ---
set "TARGET_DIR=%~1"
set "MODE=%~2"

:: If no argument is provided, prompt the user for input
if "%TARGET_DIR%"=="" (
    echo RepoLiner - Project Code Consolidator
    echo --------------------------------------------------
    echo.
    set /p "TARGET_DIR=Please enter the full path to the project directory to scan: "
    echo.
)

:: If mode was provided as argument, skip the prompt
if not "%MODE%"=="" goto :skip_mode_prompt

echo Choose Output Option:
echo [1] Standard: Save to /output folder ^(timestamped^)
echo [2] Dump:     Save to project root as 'repoliner_dump.md'
set /p "OPT=Enter choice [1-2] (Default is 1): "

set "MODE=folder"
if "%OPT%"=="2" set "MODE=dump"

:skip_mode_prompt

:: Normalize mode if passed as argument
if /i "%MODE%"=="2" set "MODE=dump"
if /i not "%MODE%"=="dump" if /i not "%MODE%"=="folder" set "MODE=folder"

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
echo.
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
echo.
echo Running RepoLiner on "%TARGET_DIR%" [Mode: %MODE%]...
echo --------------------------------------------------
python "%SCRIPT_PATH%" "%TARGET_DIR%" --mode %MODE%
echo.

echo ==================================================
echo   RepoLiner has finished.
if "%MODE%"=="dump" (
    echo   Check the selected folder for 'repoliner_dump.md'.
) else (
    echo   Check the 'output' folder for the result.
)
echo ==================================================
echo.
pause