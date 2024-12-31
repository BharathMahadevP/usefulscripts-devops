param (
    [string]$VaultName,
    [string]$EnvFile
)

# Check if required arguments are fetched correctly
if (-not $VaultName -or -not $EnvFile) {
    Write-Host "Usage: .\fetchAzureKVSecretsto_env.ps1 -VaultName <vault-name> -EnvFile <env-file>"
    exit 1
}

# Create or truncate the .env file
Write-Host "Initializing $EnvFile..."
try {
    New-Item -Path $EnvFile -ItemType File -Force | Out-Null
}
catch {
    Write-Host "Failed to create or clear $EnvFile."
    exit 1
}

# Restrict access to the .env file
try {
    icacls $EnvFile /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null
}
catch {
    Write-Host "Failed to set file permissions for $EnvFile."
    exit 1
}

# Fetch secret names
Write-Host "Fetching secrets from Key Vault: $VaultName..."
$secretNames = az keyvault secret list --vault-name $VaultName --query "[].name" -o tsv

# Check if any secrets were retrieved
if (-not $secretNames) {
    Write-Host "No secrets found in Key Vault: $VaultName."
    exit 1
}

# Write each secret as key=value to the .env file
Write-Host "Writing secrets to $EnvFile..."
foreach ($secretName in $secretNames) {
    $secretValue = az keyvault secret show --vault-name $VaultName --name $secretName --query "value" -o tsv
    if ($LASTEXITCODE -eq 0) {
        Add-Content -Path $EnvFile -Value "$secretName=$secretValue"
    }
    else {
        Write-Host "Failed to fetch value for secret: $secretName. Skipping."
    }
}

Write-Host "Secrets written to $EnvFile successfully."