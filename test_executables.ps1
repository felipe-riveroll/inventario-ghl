# PowerShell script to test Nuitka executables
# Usage: .\test_executables.ps1

Write-Host "Testing Nuitka Executables" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""

$currentDir = Get-Location
Write-Host "Current directory: $currentDir"
Write-Host ""

# Test Onefile version
$onefileExe = "dist\nuitka\InventarioGHL.exe"
if (Test-Path $onefileExe) {
    $fileInfo = Get-Item $onefileExe
    $sizeMB = [Math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "✓ Onefile executable found:" -ForegroundColor Green
    Write-Host "  Path: $onefileExe"
    Write-Host "  Size: $sizeMB MB"
    Write-Host "  Modified: $($fileInfo.LastWriteTime)"
    Write-Host ""
    
    Write-Host "Testing onefile executable..." -ForegroundColor Yellow
    $choice = Read-Host "Run onefile version? (y/N)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Write-Host "Starting: $onefileExe" -ForegroundColor Cyan
        & ".\$onefileExe"
        Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { 'Green' } else { 'Red' })
        Write-Host ""
    }
} else {
    Write-Host "✗ Onefile executable not found: $onefileExe" -ForegroundColor Red
    Write-Host "  Run: uv run python build_nuitka.py build" -ForegroundColor Yellow
    Write-Host ""
}

# Test Standalone version
$standaloneExe = "dist\main.dist\main.exe"
if (Test-Path $standaloneExe) {
    $fileInfo = Get-Item $standaloneExe
    $sizeMB = [Math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "✓ Standalone executable found:" -ForegroundColor Green
    Write-Host "  Path: $standaloneExe"
    Write-Host "  Size: $sizeMB MB"
    Write-Host "  Modified: $($fileInfo.LastWriteTime)"
    Write-Host ""
    
    Write-Host "Testing standalone executable..." -ForegroundColor Yellow
    $choice = Read-Host "Run standalone version? (y/N)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Write-Host "Starting: $standaloneExe" -ForegroundColor Cyan
        & ".\$standaloneExe"
        Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { 'Green' } else { 'Red' })
        Write-Host ""
    }
} else {
    Write-Host "✗ Standalone executable not found: $standaloneExe" -ForegroundColor Red
    Write-Host "  Run: uv run nuitka --standalone --windows-console-mode=force --enable-plugin=pyside6 --output-dir=dist main.py" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Script completed." -ForegroundColor Green