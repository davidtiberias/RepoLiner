::merge_script.bat

@echo off
cls
echo ============================================
echo   Merge Script
echo ============================================
echo.

REM --- IMPORTANT: Run this script from the project root directory. ---
cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM Define environment name
set "CONDA_ENV_NAME=base"
REM IMPORTANT: Adjust CONDA_PATH if your Conda activate.bat is in a non-standard location.
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"

REM --- Activate Conda Environment ---
echo Activating Conda environment '%CONDA_ENV_NAME%' for merging script...
call "%CONDA_PATH%"
call conda activate %CONDA_ENV_NAME%

if errorlevel 1 (
    echo ERROR: Failed to activate Conda environment '%CONDA_ENV_NAME%'.
    echo Please ensure Conda is installed and the environment exists, and that CONDA_PATH is correct.
    echo.
    echo Please resolve this issue before proceeding.
    pause > nul  REM This pause ensures you see the Conda activation error message
    goto :eof   REM Using goto :eof to prevent further execution on critical error
)

echo.
echo Conda environment '%CONDA_ENV_NAME%' activated successfully.
echo.

echo --- Environment Details ---
echo Current Conda environment: %CONDA_DEFAULT_ENV%


echo.
call python merge_script.py
echo.



echo ============================================
echo   Merge Script Complete
echo ============================================

echo.
echo Test results indicate setup status.
echo If any errors appeared, please review previous setup steps.
echo.
CMD /K
