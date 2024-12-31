# Bypass the execution policy
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Variables
$KeyVaultName = "<your-keyvault-name>"
$EnvFile = "<path-to-env-file>" #example: .env

# Check if the env file exists
if (-Not (Test-Path $EnvFile)) {
    Write-Error "Error: $EnvFile not found!"
    exit 1
}

# Read the env file and add secrets to Key Vault
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match "^(?!#)([^=]+)=(.+)$") {
        $Key = $matches[1].Trim()
        $Value = $matches[2].Trim()

        Write-Host "Adding secret: $Key"
        az keyvault secret set --vault-name $KeyVaultName --name $Key --value $Value
    }
}

Write-Host "All secrets have been added to Key Vault."
