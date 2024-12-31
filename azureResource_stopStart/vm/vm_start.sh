#!/bin/sh

echo "Validating if the VM is already deallocated..."

NAME=$1
RESOURCE_GROUP=$2

# Retrieve the current state of the VM
currentState=$(az vm get-instance-view --name "$NAME" --resource-group "$RESOURCE_GROUP" --query "instanceView.statuses[?starts_with(code, 'PowerState/')].displayStatus" -o tsv)

# Check if the current state is "VM deallocated"
if [ "$currentState" = "VM deallocated" ]; then
    echo "The VM is currently deallocated. Starting the VM..."
    az vm start -g "$RESOURCE_GROUP" -n "$NAME"
    currentState=$(az vm get-instance-view --name "$NAME" --resource-group "$RESOURCE_GROUP" --query "instanceView.statuses[?starts_with(code, 'PowerState/')].displayStatus" -o tsv)
    echo "Current state: $currentState"
else
    echo "The VM is not deallocated. Current state: $currentState"
fi
