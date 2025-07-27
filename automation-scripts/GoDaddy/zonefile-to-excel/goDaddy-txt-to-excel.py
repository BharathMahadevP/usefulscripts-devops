import pandas as pd
import re

# Read the GoDaddy zone file
with open("godaddy_zone.txt", "r") as file:
    lines = file.readlines()

# Define a dictionary to store records by type
records = {"A": [], "CNAME": [], "MX": [], "TXT": [], "NS": [], "SOA": [], "AAAA": []}

# Regex to match different DNS records
record_patterns = {
    "A": r"(\S+)\s+\d+\s+IN\s+A\s+([\d\.]+)",
    "CNAME": r"(\S+)\s+\d+\s+IN\s+CNAME\s+(\S+)",
    "MX": r"(\S+)\s+\d+\s+IN\s+MX\s+(\d+)\s+(\S+)",
    "TXT": r"(\S+)\s+\d+\s+IN\s+TXT\s+\"(.+?)\"",
    "NS": r"(\S+)\s+\d+\s+IN\s+NS\s+(\S+)",
    "SOA": r"(\S+)\s+\d+\s+IN\s+SOA\s+(\S+)\s+(\S+).*",
    "AAAA": r"(\S+)\s+\d+\s+IN\s+AAAA\s+([\da-fA-F:]+)"
}

# Parse the zone file
for line in lines:
    for record_type, pattern in record_patterns.items():
        match = re.match(pattern, line)
        if match:
            records[record_type].append(match.groups()+(record_type,))            


# Create an Excel writer object
with pd.ExcelWriter("godaddy_zone_records.xlsx", engine="openpyxl") as writer:
    for record_type, data in records.items():
        if data:  # Only create a sheet if there are records
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=record_type, index=False, header=False)

print("Excel file created successfully!")
