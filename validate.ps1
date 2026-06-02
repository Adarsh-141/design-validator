# Design Validator - Quick Run Script
# Usage: ./validate.ps1 "Your design description"

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Design,
    
    [Parameter(Mandatory=$false)]
    [string]$Output = "results/report.json",
    
    [Parameter(Mandatory=$false)]
    [string]$Model,
    
    [switch]$Verbose
)

# Build command
$cmd = "python -m src.main --design `"$Design`" --output $Output"

if ($Model) {
    $cmd += " --model $Model"
}

if ($Verbose) {
    $cmd += " --verbose"
}

Write-Host "Running: $cmd" -ForegroundColor Cyan
Write-Host ""

# Execute
Invoke-Expression $cmd
