#variables
$BufferTime = 60 #Buffer time in seconds
$containerApp = "<container-app-name>"
$resourceGroup = "<resource-group-name>"
$SubscriptionId = "<subscription-id>"


#Stop the container app
Write-Host "Stopping: $containerApp..."
Stop-AzContainerApp -Name $containerApp -ResourceGroupName $resourceGroup -SubscriptionId $SubscriptionId
Write-Host "Stopped: $containerApp"

#Allowing a buffer time for the container to stop completely
Write-Host "Allowing a buffer time of $BufferTime seconds for the container to stop completely..."
Start-Sleep -Seconds 60


#Start the container app
Write-Host "Starting: $containerApp..."
Start-AzContainerApp -Name $containerApp -ResourceGroupName $resourceGroup -SubscriptionId $SubscriptionId
Write-Host "Started: $containerApp"