from findServerDetails import finddetails


def find_details(request):
    ip = request.data
    inputType = request.inputType
    # checking if the input is a valid IP address or EC2 Instance ID
    return finddetails(ip, inputType)


