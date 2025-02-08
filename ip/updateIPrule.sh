#bin/bash

#fetch current list of ips
currentIP=$(az network nsg rule show \
    --resource-group "<resource-group>" \
    --nsg-name "<nsg-name>" \
    --name "<nsg-rule-name>" | jq '.sourceAddressPrefixes')

echo "Current IP: $currentIP"
echo "##vso[task.setvariable variable=currentIP]$currentIP"

#add ip of MS agent
echo "Adding IP of MS agent..."

az network nsg rule update \
    --resource-group "<resource-group>" \
    --nsg-name "<nsg-name>" \
    --name "<nsg-rule-name>" \
    --add sourceAddressPrefixes='["$(MS_AGENT_IP)"]'

#validating the ip range
az network nsg rule show \
    --resource-group "<resource-group>" \
    --nsg-name "<nsg-name>" \
    --name "<rule-name>" | jq '.sourceAddressPrefixes'
