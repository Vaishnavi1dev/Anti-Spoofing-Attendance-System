@echo off
echo ========================================
echo Smart Classroom Migration Helper
echo ========================================
echo.
echo This script will help you migrate to a fresh repository.
echo.
echo Before running, make sure you have:
echo 1. Created a new empty repository on GitHub
echo 2. Copied the repository URL
echo.
pause
echo.
set /p REPO_URL="Enter your new repository URL: "
echo.
echo Starting migration...
echo.
powershell -ExecutionPolicy Bypass -File migrate-to-fresh-repo.ps1 -NewRepoUrl "%REPO_URL%"
echo.
pause
