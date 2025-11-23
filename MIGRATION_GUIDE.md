# Migration Guide: Creating Fresh Repository

## Step-by-Step Instructions

### Option 1: Using Git Commands (Recommended)

#### 1. Create New Repository on GitHub
1. Go to GitHub.com
2. Click "New Repository"
3. Name it (e.g., "smart-classroom-attendance")
4. **DO NOT** initialize with README, .gitignore, or license
5. Copy the repository URL

#### 2. Clone Current Repository to New Location
```bash
# Navigate to parent directory
cd C:\Users\vishu\Desktop

# Clone current repo to new folder
git clone https://github.com/Udbhav2025/HT-100-CV-009.git smart-classroom-fresh

# Enter new folder
cd smart-classroom-fresh
```

#### 3. Remove Old Git History and Create Fresh
```bash
# Remove old git history
Remove-Item -Recurse -Force .git

# Initialize new git repository
git init

# Add all files
git add -A

# Create initial commit
git commit -m "Initial commit: Smart Classroom Attendance System"

# Add new remote (replace with your new repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git

# Push to new repository
git branch -M main
git push -u origin main
```

### Option 2: Manual Copy (Alternative)

#### 1. Create New Folder
```bash
# Create new folder
cd C:\Users\vishu\Desktop
mkdir smart-classroom-fresh
cd smart-classroom-fresh
```

#### 2. Copy Files (Excluding Git History)
```bash
# Copy all files except .git folder
robocopy C:\Users\vishu\Desktop\udbhav . /E /XD .git node_modules __pycache__ .next build dist
```

#### 3. Initialize Git
```bash
# Initialize git
git init

# Add all files
git add -A

# Create initial commit
git commit -m "Initial commit: Smart Classroom Attendance System"

# Add remote (replace with your new repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git

# Push
git branch -M main
git push -u origin main
```

### Option 3: Using PowerShell Script

Save this as `migrate.ps1` and run it:

```powershell
# Configuration
$currentRepo = "C:\Users\vishu\Desktop\udbhav"
$newFolder = "C:\Users\vishu\Desktop\smart-classroom-fresh"
$newRepoUrl = "https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git"

# Create new folder
New-Item -ItemType Directory -Path $newFolder -Force
Set-Location $newFolder

# Copy files (excluding git and build folders)
$excludeDirs = @('.git', 'node_modules', '__pycache__', '.next', 'build', 'dist', 'temp_db*', 'unknown_faces', 'photos')
Get-ChildItem -Path $currentRepo -Recurse | Where-Object {
    $item = $_
    $exclude = $false
    foreach ($dir in $excludeDirs) {
        if ($item.FullName -like "*\$dir\*" -or $item.Name -eq $dir) {
            $exclude = $true
            break
        }
    }
    -not $exclude
} | Copy-Item -Destination {
    $dest = $_.FullName.Replace($currentRepo, $newFolder)
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    $dest
} -Force

# Initialize git
git init
git add -A
git commit -m "Initial commit: Smart Classroom Attendance System"
git remote add origin $newRepoUrl
git branch -M main
git push -u origin main

Write-Host "Migration complete!" -ForegroundColor Green
```

## What Gets Copied

### ✅ Include (Will be copied)
- All source code files
- Documentation (*.md files)
- Configuration files (.env, package.json, etc.)
- Requirements files
- Scripts and utilities
- Frontend assets
- Backend modules

### ❌ Exclude (Will NOT be copied)
- `.git/` - Old git history
- `node_modules/` - Frontend dependencies (reinstall)
- `__pycache__/` - Python cache
- `temp_db*/` - Temporary databases
- `unknown_faces/` - Unknown face images
- `photos/` - Uploaded photos (optional)
- Build artifacts

## After Migration

### 1. Update Repository References
Edit these files to update repository URLs:
- `README.md` - Update clone URL
- `package.json` - Update repository field
- Any documentation with old repo links

### 2. Setup Fresh Environment

**Backend**:
```bash
cd backend
pip install -r requirements.txt
python setup_database_mongo.py
python create_admin.py
```

**Frontend**:
```bash
cd frontend
npm install
```

### 3. Configure Environment
```bash
# Copy and edit .env
cd backend
cp .env.example .env
# Edit .env with your settings
```

### 4. Test Everything
```bash
# Start backend
cd backend
python main.py

# Start frontend (new terminal)
cd frontend
npm start

# Access: http://localhost:3000
```

## Clean Repository Structure

Your new repository will have:
```
smart-classroom-fresh/
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database_mongo.py
│   ├── liveness_detection.py
│   ├── requirements.txt
│   └── ... (all backend files)
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ... (all frontend files)
├── README.md
├── .gitignore
└── ... (documentation files)
```

## Verification Checklist

After migration, verify:
- [ ] All source files present
- [ ] README.md is correct
- [ ] .gitignore is present
- [ ] Backend requirements.txt exists
- [ ] Frontend package.json exists
- [ ] Documentation files included
- [ ] No .git folder from old repo
- [ ] No node_modules or __pycache__
- [ ] Git remote points to new repo
- [ ] Can install dependencies
- [ ] Can run backend
- [ ] Can run frontend

## Troubleshooting

### Issue: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin YOUR_NEW_REPO_URL
```

### Issue: "Permission denied"
```bash
# Use HTTPS with token or SSH key
git remote set-url origin https://YOUR_TOKEN@github.com/USER/REPO.git
```

### Issue: Files not copying
```bash
# Check if source exists
Test-Path C:\Users\vishu\Desktop\udbhav

# Use absolute paths
robocopy "C:\Users\vishu\Desktop\udbhav" "C:\Users\vishu\Desktop\smart-classroom-fresh" /E /XD .git
```

## Quick Command Summary

```bash
# Quick migration (one-liner)
cd C:\Users\vishu\Desktop && `
git clone https://github.com/Udbhav2025/HT-100-CV-009.git smart-classroom-fresh && `
cd smart-classroom-fresh && `
Remove-Item -Recurse -Force .git && `
git init && `
git add -A && `
git commit -m "Initial commit: Smart Classroom Attendance System" && `
git remote add origin YOUR_NEW_REPO_URL && `
git branch -M main && `
git push -u origin main
```

## Notes

1. **Backup First**: Keep original repo until migration is verified
2. **Clean Start**: Fresh git history, no old commits
3. **Dependencies**: Need to reinstall node_modules and Python packages
4. **Database**: Need to setup MongoDB fresh
5. **Photos**: Upload student photos again (or copy photos/ folder)
6. **Environment**: Configure .env with your settings

## Support

If you encounter issues:
1. Check file paths are correct
2. Ensure you have write permissions
3. Verify git is installed
4. Check GitHub authentication
5. Review error messages carefully

---

**Ready to migrate? Follow Option 1 for the cleanest approach!**
