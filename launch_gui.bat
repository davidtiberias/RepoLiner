@echo off
cls

:: =================================================================
:: RepoLiner GUI - Web Interface Launcher
:: =================================================================
:: This script starts the RepoLiner GUI web server.
:: It will open your browser to http://localhost:5000 automatically.
:: =================================================================

:: --- Configuration ---
set "CONDA_ENV_NAME=repoliner-env"
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"
set "SCRIPT_PATH=%~dp0scripts\gui_server.py"

echo.
echo  =============================================
echo   RepoLiner GUI - Starting...
echo  =============================================
echo.

:: --- Activate Conda Environment (silently) ---
echo  Activating Conda environment '%CONDA_ENV_NAME%'...
call "%CONDA_PATH%" > nul 2>&1
call conda activate %CONDA_ENV_NAME% > nul 2>&1

if errorlevel 1 (
    echo.
    echo  ERROR: Failed to activate Conda environment '%CONDA_ENV_NAME%'.
    echo  Please ensure it was created with 'conda env create -f environment.yml'.
    echo.
    pause
    goto :eof
)

:: --- Run the GUI Server ---
echo  Starting web server...
echo  Open your browser at: http://localhost:5000
echo.
echo  Press Ctrl+C to stop the server.
echo  =============================================
echo.
python "%SCRIPT_PATH%"
pause
