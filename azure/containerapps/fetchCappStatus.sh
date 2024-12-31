containerApp="<containerAppName>"
resourceGroup="<resourceGroupName>"

echo "Validating if the container is Up and Running..."

currentState=""
while [ "$currentState" != "Running" ]; do
    currentState=$(az containerapp show --name $containerApp --resource-group $resourceGroup | grep '"runningStatus"' | sed 's/.*"runningStatus": "\(.*\)",.*/\1/')
    echo "Current Provisioning State of $containerApp: $currentState"
    sleep 5
done

echo "Started: $containerApp"
