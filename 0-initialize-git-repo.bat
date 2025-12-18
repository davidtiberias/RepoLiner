@echo off
cls

:: =================================================================
:: RepoLiner Setup - Step 0: Initialize Git Repository
:: =================================================================
:: This script will:
:: 1. Check if Git is installed.
:: 2. Initialize a new Git repository in this folder if one doesn't exist.
:: =================================================================
echo.
echo RepoLiner Setup - Step 0: Initializing Git Repository
echo ----------------------------------------------------
echo.

:: --- Check if Git is installed ---
git --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or cannot be found on your system's PATH.
    echo Please install Git for Windows from https://git-scm.com/download/win
    echo and ensure you select the 'Recommended' option for the PATH during installation.
    pause
    goto :eof
)

:: --- Check if this is already a Git repository ---
if exist .git (
    echo This directory is already a Git repository.
    echo Skipping initialization.
    echo.
    pause
    goto :eof
)

:: --- Initialize the repository and make the first commit ---
echo Initializing a new Git repository...
git init
echo.
echo Adding all project files to the repository...
git add .
echo.
echo Creating the initial commit...
git commit -m "Initial commit: Set up RepoLiner project structure"

echo.
echo ===================================================================
echo   SUCCESS: Git repository has been created.
echo ===================================================================
echo.
echo You can now proceed with the other setup steps.
echo.
pause