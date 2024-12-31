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

# Read the env file and remove it from keyvault
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match "^(?!#)([^=]+)=(.+)$") {
        $SecretName = $matches[1].Trim()

        Write-Host "Removing secret: $SecretName"
        az keyvault secret delete --vault-name $KeyVaultName --name $SecretName
    }
}

Write-Host "All secrets have been removed from $KeyVaultName Key Vault."
