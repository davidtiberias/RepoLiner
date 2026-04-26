@echo off
cls

:: =================================================================
:: RepoLiner Utility - Pre-Commit Hook Manager (for Contributors)
:: =================================================================
:: This script allows you to manage the Git hooks powered by pre-commit.
:: Pre-commit automatically checks your code quality on every commit.
:: =================================================================
echo.
echo RepoLiner - Pre-Commit Hook Manager
echo -------------------------------------
echo.

:: --- Prerequisite Check: Ensure Git is installed and this is a repo ---
git --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in your PATH.
    echo Pre-commit requires Git to function. Please install it from https://git-scm.com/
    pause
    goto :eof
)
if not exist .git (
    echo ERROR: This is not a Git repository.
    echo Please run '0-initialize-git-repo.bat' first.
    pause
    goto :eof
)

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

:menu
cls
echo RepoLiner - Pre-Commit Hook Manager
echo -------------------------------------
echo What would you like to do?
echo.
echo   1. Install Hooks (Required for contributing)
echo   2. Run on All Files (Manually check the whole project)
echo   3. Uninstall Hooks
echo   4. Exit
echo.
set /p "CHOICE=Enter your choice (1-4): "

if "%CHOICE%"=="1" goto :install
if "%CHOICE%"=="2" goto :run_all
if "%CHOICE%"=="3" goto :uninstall
if "%CHOICE%"=="4" goto :eof
echo Invalid choice.
pause
goto :menu

:install
echo.
echo --- Installing pre-commit hooks... ---
pre-commit install
echo.
echo SUCCESS: The pre-commit hooks are now installed.
echo Checks will run automatically every time you commit.
pause
goto :eof

:run_all
echo.
echo --- Running pre-commit on all project files... ---
pre-commit run --all-files
echo.
echo Finished. Review any changes above.
pause
goto :eof

:uninstall
echo.
echo --- Uninstalling pre-commit hooks... ---
pre-commit uninstall
echo.
echo SUCCESS: The pre-commit hooks have been removed.
pause
goto :eof