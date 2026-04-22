# LANForge Burn-In Deployment Script
# Automatically downloads LibreHardwareMonitor, starts it to initialize WMI temperature sensors,
# and then launches the LANForge Burn-In Tester.

$ErrorActionPreference = "Stop"

Write-Host "Setting up LANForge Burn-In Test Environment..." -ForegroundColor Cyan

# 1. Download and extract LibreHardwareMonitor
$lhmZipPath = "$PSScriptRoot\LibreHardwareMonitor.zip"
$lhmExtractedPath = "$PSScriptRoot\LibreHardwareMonitor"
# Using a stable, recent release URL
$lhmUrl = "https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/download/v0.9.3/LibreHardwareMonitor-0.9.3.zip"

if (-not (Test-Path "$lhmExtractedPath\LibreHardwareMonitor.exe")) {
    Write-Host "Downloading LibreHardwareMonitor for accurate WMI sensors..."
    Invoke-WebRequest -Uri $lhmUrl -OutFile $lhmZipPath
    
    Write-Host "Extracting LibreHardwareMonitor..."
    Expand-Archive -Path $lhmZipPath -DestinationPath $lhmExtractedPath -Force
    Remove-Item $lhmZipPath
}

# 2. Start LibreHardwareMonitor (creates the root\LibreHardwareMonitor WMI namespace)
Write-Host "Starting LibreHardwareMonitor..."
Start-Process -FilePath "$lhmExtractedPath\LibreHardwareMonitor.exe" -WindowStyle Hidden

Write-Host "Waiting for WMI sensors to populate..."
Start-Sleep -Seconds 5

# 3. Start the LANForge Burn-In App
$burnInExe = "$PSScriptRoot\dist\main.exe"

if (Test-Path $burnInExe) {
    Write-Host "Launching packaged LANForge Burn-In Tester..." -ForegroundColor Green
    Start-Process -FilePath $burnInExe
} else {
    Write-Host "Packaged main.exe not found in dist folder. Falling back to Python..." -ForegroundColor Yellow
    # Ensure dependencies exist if running raw
    Write-Host "Launching Python script..." -ForegroundColor Green
    Start-Process -FilePath "python" -ArgumentList "$PSScriptRoot\src\main.py"
}
