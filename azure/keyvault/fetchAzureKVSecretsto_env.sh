#!/bin/bash

# Variables
VAULT_NAME="$1"
ENV_FILE="$2"

# Check if required arguments are fetched correctly
if [ -z "$VAULT_NAME" ] || [ -z "$ENV_FILE" ]; then
    echo "Usage: $0 <vault-name> <env-file>"
    exit 1
fi

# Create or truncate the .env file
echo "Initializing $ENV_FILE..."
>"$ENV_FILE" || {
    echo "Failed to create or clear $ENV_FILE."
    exit 1
}

# Restrict access to the .env file
chmod 600 "$ENV_FILE" || {
    echo "Failed to set file permissions for $ENV_FILE."
    exit 1
}

# Fetch secret names
echo "Fetching secrets from Key Vault: $VAULT_NAME..."
SECRET_NAMES=$(az keyvault secret list --vault-name "$VAULT_NAME" --query "[].name" -o tsv)

# Check if any secrets were retrieved
if [ -z "$SECRET_NAMES" ]; then
    echo "No secrets found in Key Vault: $VAULT_NAME."
    exit 1
fi

# Write each secret as key=value to the .env file
echo "Writing secrets to $ENV_FILE..."
for SECRET_NAME in $SECRET_NAMES; do
    SECRET_VALUE=$(az keyvault secret show --vault-name "$VAULT_NAME" --name "$SECRET_NAME" --query "value" -o tsv)
    if [ $? -eq 0 ]; then
        echo "$SECRET_NAME=$SECRET_VALUE" >>"$ENV_FILE"
    else
        echo "Failed to fetch value for secret: $SECRET_NAME. Skipping."
    fi
done

echo "Secrets written to $ENV_FILE successfully."
