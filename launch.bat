@echo off
setlocal
cls

:: =================================================================
:: RepoLiner - Unified Launcher
:: =================================================================
:: This script is the single entry point for RepoLiner. It can:
:: 1. Be run with arguments for direct CLI execution:
::    > launch.bat "C:\path\to\project" [folder|dump]
:: 2. Be double-clicked to show a menu for GUI or CLI.
:: =================================================================

:: --- Configuration ---
set "CONDA_ENV_NAME=repoliner-env"
set "CONDA_PATH=%UserProfile%\miniconda3\Scripts\activate.bat"
set "CLI_SCRIPT_PATH=%~dp0scripts\merge_cli.py"
set "GUI_SCRIPT_PATH=%~dp0scripts\gui_server.py"

:: --- Flow Control: Check if arguments were passed for direct CLI use ---
if not "%~1"=="" (
    call :run_cli_direct %*
    goto :eof
)

:: --- If no arguments, show the main menu ---
:menu
cls
echo.
echo  =============================================
echo       RepoLiner - Code Consolidator
echo  =============================================
echo.
echo  Choose an option:
echo.
echo    1. Launch Graphical User Interface (GUI)
echo    2. Launch Command-Line (Interactive Prompts)
echo    3. Open Command-Line (Power-User Mode)
echo    4. Exit
echo.
set /p "CHOICE=Enter your choice [1-4]: "

if "%CHOICE%"=="1" goto :launch_gui
if "%CHOICE%"=="2" goto :launch_cli_interactive
if "%CHOICE%"=="3" goto :launch_cli_poweruser
if "%CHOICE%"=="4" goto :eof
echo Invalid choice.
pause
goto :menu


:: =================================================================
::  Subroutines
:: =================================================================

:launch_gui
    echo.
    echo --- Launching GUI ---
    call :activate_env
    if errorlevel 1 goto :eof
    echo Starting web server... Open your browser at http://localhost:5000
    python "%GUI_SCRIPT_PATH%"
    pause
    goto :eof

:launch_cli_interactive
    echo.
    echo --- CLI Interactive Mode ---
    echo.
    set /p "TARGET_DIR=Enter the full path to your project: "
    echo.
    echo Choose Output Mode:
    echo   [1] Standard (Save to /output folder)
    echo   [2] Dump (Save to project root as 'repoliner_dump.md')
    set /p "OPT=Enter choice [1-2] (Default is 1): "
    
    set "MODE=folder"
    if "%OPT%"=="2" set "MODE=dump"

    :: Pass the collected variables to the direct execution subroutine
    call :run_cli_direct "%TARGET_DIR%" %MODE%
    goto :eof

:launch_cli_poweruser
    echo.
    echo --- CLI Power-User Mode ---
    call :activate_env
    if errorlevel 1 goto :eof
    echo You are now in the RepoLiner CLI environment.
    echo.
    echo Usage: python scripts\merge_cli.py "C:\path\to\your\project" --mode [folder^|dump]
    echo.
    cmd /k
    goto :eof

:run_cli_direct
    set "TARGET_DIR=%~1"
    set "MODE=%~2"

    :: --- Validate Input ---
    if not exist "%TARGET_DIR%" (
        echo.
        echo ERROR: The specified directory does not exist:
        echo "%TARGET_DIR%"
        pause
        goto :eof
    )

    :: --- Normalize Mode ---
    if /i "%MODE%"=="" set "MODE=folder"
    if /i "%MODE%"=="dump" (set "MODE=dump") else (set "MODE=folder")

    :: --- Activate Environment & Run ---
    echo.
    echo Activating environment and running RepoLiner...
    call :activate_env
    if errorlevel 1 goto :eof
    
    echo.
    echo Running on "%TARGET_DIR%" [Mode: %MODE%]
    echo --------------------------------------------------
    python "%CLI_SCRIPT_PATH%" "%TARGET_DIR%" --mode %MODE%
    echo.

    echo ==================================================
    echo   RepoLiner has finished.
    if "%MODE%"=="dump" (
        echo   Check for 'repoliner_dump.md' in the project folder.
    ) else (
        echo   Check the 'output' folder for the result.
    )
    echo ==================================================
    echo.
    pause
    goto :eof

:activate_env
    if not exist "%CONDA_PATH%" (
        echo ERROR: Miniconda not found at "%CONDA_PATH%". Please run the setup scripts.
        pause
        exit /b 1
    )
    call "%CONDA_PATH%" > nul 2>&1
    call conda activate %CONDA_ENV_NAME% > nul 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to activate Conda environment '%CONDA_ENV_NAME%'. Please run setup.
        pause
        exit /b 1
    )
    exit /b 0