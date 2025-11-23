# Smart Classroom Attendance System - Repository Migration Script
# This script creates a fresh repository with all files but no git history

param(
    [Parameter(Mandatory=$true)]
    [string]$NewRepoUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$NewFolderName = "smart-classroom-fresh"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Smart Classroom Migration Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$currentPath = Get-Location
$parentPath = Split-Path $currentPath -Parent
$newPath = Join-Path $parentPath $NewFolderName

Write-Host "Current repository: $currentPath" -ForegroundColor Yellow
Write-Host "New repository will be created at: $newPath" -ForegroundColor Yellow
Write-Host "New remote URL: $NewRepoUrl" -ForegroundColor Yellow
Write-Host ""

# Confirm
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Migration cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Step 1: Creating new folder..." -ForegroundColor Green

# Create new folder
if (Test-Path $newPath) {
    Write-Host "Warning: Folder already exists. Removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $newPath
}
New-Item -ItemType Directory -Path $newPath -Force | Out-Null

Write-Host "Step 2: Copying files..." -ForegroundColor Green

# Folders to exclude
$excludeDirs = @(
    '.git',
    'node_modules',
    '__pycache__',
    '.next',
    'build',
    'dist',
    'temp_db*',
    'unknown_faces'
)

# Files to exclude
$excludeFiles = @(
    '*.pyc',
    '.DS_Store',
    'Thumbs.db'
)

# Copy files
$itemsCopied = 0
Get-ChildItem -Path $currentPath -Recurse -Force | Where-Object {
    $item = $_
    $exclude = $false
    
    # Check if in excluded directory
    foreach ($dir in $excludeDirs) {
        if ($item.FullName -like "*\$dir\*" -or $item.FullName -like "*\$dir" -or $item.Name -eq $dir) {
            $exclude = $true
            break
        }
    }
    
    # Check if excluded file type
    if (-not $exclude) {
        foreach ($pattern in $excludeFiles) {
            if ($item.Name -like $pattern) {
                $exclude = $true
                break
            }
        }
    }
    
    -not $exclude
} | ForEach-Object {
    $dest = $_.FullName.Replace($currentPath, $newPath)
    
    if ($_.PSIsContainer) {
        # Create directory
        if (-not (Test-Path $dest)) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
        }
    } else {
        # Copy file
        $destDir = Split-Path $dest -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -Path $_.FullName -Destination $dest -Force
        $itemsCopied++
    }
}

Write-Host "Copied $itemsCopied files" -ForegroundColor Cyan

Write-Host "Step 3: Initializing git repository..." -ForegroundColor Green

# Change to new directory
Set-Location $newPath

# Initialize git
git init | Out-Null

# Add all files
git add -A

# Create initial commit
git commit -m "Initial commit: Smart Classroom Attendance System with Face Recognition and Anti-Spoofing" | Out-Null

# Add remote
git remote add origin $NewRepoUrl

# Set branch to main
git branch -M main

Write-Host "Step 4: Pushing to remote repository..." -ForegroundColor Green

# Push to remote
try {
    git push -u origin main
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Migration completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "New repository location: $newPath" -ForegroundColor Cyan
    Write-Host "Remote URL: $NewRepoUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. cd $newPath" -ForegroundColor White
    Write-Host "2. cd backend && pip install -r requirements.txt" -ForegroundColor White
    Write-Host "3. cd frontend && npm install" -ForegroundColor White
    Write-Host "4. Setup database: python backend/setup_database_mongo.py" -ForegroundColor White
    Write-Host "5. Create admin: python backend/create_admin.py" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "Error pushing to remote: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Repository created locally at: $newPath" -ForegroundColor Yellow
    Write-Host "You can push manually with: git push -u origin main" -ForegroundColor Yellow
}

# Return to original directory
Set-Location $currentPath
