@echo off
cls

:: =================================================================
:: RepoLiner Utility - Run All Quality Checks (No Git Required)
:: =================================================================
:: This script will manually:
:: 1. Check code formatting with Black.
:: 2. Check for errors and style issues with Flake8.
:: =================================================================
echo.
echo RepoLiner - Running All Code Quality Checks
echo ---------------------------------------------
echo.

:: --- Configuration ---
set "CONDA_ENV_NAME=repoliner-env"
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"

:: --- Activate the Conda Environment ---
echo Activating the '%CONDA_ENV_NAME%' environment...
call "%CONDA_PATH%"
call conda activate %CONDA_ENV_NAME%

if errorlevel 1 (
    echo ERROR: Failed to activate the Conda environment.
    pause
    goto :eof
)

set "error_found=0"

:: --- 1. Check formatting with Black ---
echo.
echo [1/2] Checking code formatting with Black...
echo --------------------------------------------
black . --check

if errorlevel 1 (
    echo.
    echo WARNING: Black found formatting issues.
    echo To fix them automatically, run the command: black .
    echo.
    set "error_found=1"
) else (
    echo OK: All files are formatted correctly.
    echo.
)


:: --- 2. Check for errors with Flake8 ---
echo [2/2] Checking for errors with Flake8...
echo ------------------------------------------
flake8 .

if errorlevel 1 (
    echo.
    echo WARNING: Flake8 found potential errors or style violations above.
    echo Please review and fix them manually.
    echo.
    set "error_found=1"
) else (
    echo OK: No issues found by Flake8.
    echo.
)


:: --- Final Summary ---
echo ===================================================================
if %error_found%==1 (
    echo   Finished: One or more quality checks failed. Please review the output.
) else (
    echo   Finished: All quality checks passed successfully!
)
echo ===================================================================
echo.
pause