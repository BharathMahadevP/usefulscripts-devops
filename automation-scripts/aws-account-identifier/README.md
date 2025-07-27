# Account Finder

This is a Python script used to find the details of an EC2 instance.

#### Objective of writing this script

When managing multiple AWS accounts, it can be challenging for the team to locate the specific details of an EC2 instance. This script is designed to simplify that process by quickly retrieving the instance information across accounts.

## Prerequisites

- Python must be installed and properly set up on the machine.
- AWS CLI must be configured on the local machine where the script will be executed, with appropriate access. (Multi profile setup is required.)

## Steps to execute script

> Make sure all the prerequisites listed above are fulfilled before proceeding.

1. Clone this repository

```bash
git clone https://github.com/BharathMahadevP/usefulscripts-devops.git
```

2. Switch to the code directory

```bash
cd aws-account-identifier/
```

3. Install necessary python modules

```bash
pip install boto3
```

4. Execute the script

- For finding server details using public ip

```bash
python3 accountFinder-public-ip.py
```

- For finding server details using private ip

```bash
python3 accountFinder-private-ip.py
```

> Type pyth and press Tab button. This will autofill with the current python installed on your system.
