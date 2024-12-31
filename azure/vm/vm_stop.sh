#!/bin/sh

echo "Validating if the VM is already stopped..."

NAME=$1
RESOURCE_GROUP=$2

# Retrieve the current state of the VM
currentState=$(az vm get-instance-view --name "$NAME" --resource-group "$RESOURCE_GROUP" --query "instanceView.statuses[?starts_with(code, 'PowerState/')].displayStatus" -o tsv)

# Check if the current state is not "VM running"
if [ "$currentState" = "VM running" ]; then
    echo "The VM is currently running. Deallocating the VM..."
    az vm deallocate -g "$RESOURCE_GROUP" -n "$NAME"
    currentState=$(az vm get-instance-view --name "$NAME" --resource-group "$RESOURCE_GROUP" --query "instanceView.statuses[?starts_with(code, 'PowerState/')].displayStatus" -o tsv)
    echo "Current state: $currentState"
else
    echo "The VM is not running. Current state: $currentState"
fi
