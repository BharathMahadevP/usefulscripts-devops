$folderPath = $env:TEMP
$timestamp  = Get-Date -Format "dd-MM-yyyy HH:mm:ss"
$logFile    = Join-Path $PSScriptRoot "ClearTemp.log"

function Write-Log {
    param([string]$Message)
    $entry = "$timestamp : $Message"
    Write-Output $entry
    Add-Content -Path $logFile -Value $entry
}

if (Test-Path $folderPath) {
    $items = Get-ChildItem -Path $folderPath -Recurse -Force -ErrorAction SilentlyContinue
    $totalCount   = $items.Count
    $failedCount  = 0

    foreach ($item in $items) {
        try {
            Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction Stop
        }
        catch {
            $failedCount++
        }
    }

    $deletedCount = $totalCount - $failedCount
    Write-Log "Cleared $deletedCount of $totalCount items in '$folderPath'. ($failedCount skipped - in use or locked)."
}
else {
    Write-Log "The folder path '$folderPath' does not exist."
}
