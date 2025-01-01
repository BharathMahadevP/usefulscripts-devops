#Parameters
$Days = "14" # Number of days to be cosidered for deletion
$RemoveCount = 0
$FileWildCard = "*.txt" # File extension to be removed

# Path where the file is located
$sourceFolder = $PSScriptRoot
Write-Host "Source Path: $sourceFolder"

#Calculate Cutoff date
$CutoffDate = (Get-Date).AddDays(-$Days)
$sourceItems = (Get-ChildItem $sourceFolder | Where-Object { $_.Name -like $FileWildCard } | Measure-Object ).count
Write-Host "Total count of filtered files : $sourceItems"

if ($sourceItems -gt 0) {
    Write-Host "Removing files older than $Days days"
    $RemoveCount = (Get-ChildItem $sourceFolder | Where-Object { $_.Name -like $FileWildCard } | Where-Object { $_.LastWriteTime -lt $CutoffDate } | Measure-Object ).count
    Get-ChildItem $sourceFolder | Where-Object { $_.Name -like $FileWildCard } | Where-Object { $_.LastWriteTime -lt $CutoffDate } | Remove-Item –Force -Verbose
}
Write-Output "$(Get-Date) Files Deleted Sucessfully : $RemoveCount" >> "log_$(Get-Date -Format 'dd_MM_yyyy').txt"