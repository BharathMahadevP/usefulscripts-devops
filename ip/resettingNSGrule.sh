echo "Initial ip range: $(currentIP)"

echo "Removing IP of MS agent..."

az network nsg rule update \
    --resource-group "<resource-group>" \
    --nsg-name "<nsg-name>" \
    --name "<nsg-rule-name>" \
    --set sourceAddressPrefixes='$(currentIP)'