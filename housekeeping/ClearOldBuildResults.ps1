<#
.SYNOPSIS
    Clears old build result folders, keeping only the latest N folders.

.DESCRIPTION
    This script scans a target directory, counts the top-level folders,
    and deletes the oldest ones — keeping only the most recent 5 (by default).
    Age is determined by the folder's LastWriteTime.

.PARAMETER TargetPath
    The path to the directory containing build result folders.

.PARAMETER KeepCount
    The number of most-recent folders to retain. Defaults to 5.

.PARAMETER WhatIf
    Preview which folders would be deleted without actually removing them.

.EXAMPLE
    .\ClearOldBuildResults.ps1 -TargetPath "D:\Builds\Output"

.EXAMPLE
    .\ClearOldBuildResults.ps1 -TargetPath "D:\Builds\Output" -KeepCount 3

.EXAMPLE
    .\ClearOldBuildResults.ps1 -TargetPath "D:\Builds\Output" -WhatIf
#>

param (
    [Parameter(Mandatory = $true, HelpMessage = "Path to the folder containing build result directories.")]
    [ValidateScript({ Test-Path $_ -PathType Container })]
    [string]$TargetPath,

    [Parameter(HelpMessage = "Number of latest folders to keep. Default is 5.")]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$KeepCount = 5
)

# ── Retrieve all top-level folders ───────────────────────────────────────────
$allFolders = Get-ChildItem -Path $TargetPath -Directory

$totalCount = $allFolders.Count

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Target Path  : $TargetPath"                                -ForegroundColor Cyan
Write-Host "  Total Folders : $totalCount"                               -ForegroundColor Cyan
Write-Host "  Keep Latest   : $KeepCount"                                -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Nothing to do if folder count is within the keep limit ───────────────────
if ($totalCount -le $KeepCount) {
    Write-Host "Only $totalCount folder(s) found. Nothing to delete..." -ForegroundColor Green
    exit 0
}

# ── Sort folders by LastWriteTime descending and pick the ones to remove ─────
$sortedFolders = $allFolders | Sort-Object LastWriteTime -Descending
$foldersToKeep = $sortedFolders | Select-Object -First $KeepCount
$foldersToDelete = $sortedFolders | Select-Object -Skip $KeepCount

$deleteCount = $foldersToDelete.Count

Write-Host "Folders to KEEP ($KeepCount latest):" -ForegroundColor Green
foreach ($folder in $foldersToKeep) {
    Write-Host "$($folder.Name)  (Last Modified: $($folder.LastWriteTime))" -ForegroundColor Green
}

Write-Host ""
Write-Host "Folders to DELETE ($deleteCount older):" -ForegroundColor Yellow
foreach ($folder in $foldersToDelete) {
    Write-Host "$($folder.Name)  (Last Modified: $($folder.LastWriteTime))" -ForegroundColor Yellow
}

Write-Host ""

# ── Delete the old folders ───────────────────────────────────────────────────
$deletedCount = 0
$failedCount = 0

foreach ($folder in $foldersToDelete) {
    try {
        Remove-Item -Path $folder.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "Deleted: $($folder.FullName)" -ForegroundColor DarkGreen
        $deletedCount++
    }
    catch {
        Write-Warning "Failed to delete: $($folder.FullName) — $_"
        $failedCount++
    }
}

# ── Summary ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Deleted : $deletedCount folder(s)" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "  Failed  : $failedCount folder(s)" -ForegroundColor Red
}
Write-Host "  Kept    : $KeepCount folder(s)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
