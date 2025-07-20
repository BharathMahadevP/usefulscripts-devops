# Fetch and restrict IP to the host
ip=$(curl -s https://ipinfo.io/ip | tr -d '[:space:]')

# Assign it as a pipeline variable
echo "Setting the IP address as an pipeline variable..."
echo "Variable Name: MS_AGENT_IP"
echo "##vso[task.setvariable variable=MS_AGENT_IP]$ip"

# Display the IP address
echo "IP address of current agent: $ip"