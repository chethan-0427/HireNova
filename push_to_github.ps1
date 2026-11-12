# HireNova - GitHub Deploy Automation Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  HireNova - Push to GitHub (chethan-0427/HireNova)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check if user is authenticated with gh
$ghAuth = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nGitHub CLI is not logged in." -ForegroundColor Yellow
    Write-Host "Option 1: Paste a Personal Access Token (classic with 'repo' scope from https://github.com/settings/tokens/new)" -ForegroundColor Green
    Write-Host "Option 2: Press Enter to open GitHub in browser to create the repo manually`n" -ForegroundColor Green
    
    $token = Read-Host "Paste token (or press Enter to create repo via web)"
    if ($token.Trim() -ne "") {
        Write-Host "Authenticating with token..." -ForegroundColor Yellow
        $token.Trim() | gh auth login --with-token
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Authenticated successfully with GitHub CLI!" -ForegroundColor Green
            Write-Host "Creating remote repository chethan-0427/HireNova..." -ForegroundColor Yellow
            gh repo create HireNova --public --source=. --remote=origin
        }
    } else {
        Write-Host "Opening https://github.com/new in your browser..." -ForegroundColor Yellow
        Start-Process "https://github.com/new?name=HireNova&description=Online+Job+Portal+Web+Application+-+Minor+Project+Internship+Submission&visibility=public"
        Write-Host "Click 'Create repository' in your browser (do NOT add README/license), then press Enter here." -ForegroundColor Yellow
        Pause
    }
} else {
    Write-Host "Authenticated with GitHub CLI!" -ForegroundColor Green
    # Check if repo exists
    gh repo view chethan-0427/HireNova 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating remote repository..." -ForegroundColor Yellow
        gh repo create HireNova --public --source=. --remote=origin
    }
}

# 2. Push all branches and tags
Write-Host "`nPushing main branch with tags..." -ForegroundColor Cyan
git push -u origin main --tags

Write-Host "`nPushing dev branch..." -ForegroundColor Cyan
git push origin dev

Write-Host "`nPushing feature branches..." -ForegroundColor Cyan
git push origin feature/database-setup feature/backend feature/frontend feature/documentation

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Live Repository URL:" -ForegroundColor Green
Write-Host "  https://github.com/chethan-0427/HireNova" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green

