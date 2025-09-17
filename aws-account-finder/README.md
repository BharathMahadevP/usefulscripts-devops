# The EC2 Instance Details Finder

#### Use Case:

In scenarios where the team has to interact with multiple AWS accounts it can become quite difficult for the team to identify or find the details of EC2 instances if they only have very limited information say, the public ip of the instance or the instance id.

This tool can be used in such scenarios to fetch the details of EC2 instances.
As an input the tool requires **'any'** of the following:

1. The Public IP of the Instance
2. The Private IP of the instance
3. The instance ID

### Tech Stacks Used:

- #### Front End:

1.  HTML
2.  CSS
3.  Javascript

- #### Backend:

1. Python
   - Fast API
   - Boto3
2. Docker

- #### Webserver:

  - Apache

- #### AWS Access
  - Client ID and Client Secret

## Prerequisites

- Python
- Docker
- IAM user with permission: **AmazonEC2ReadOnlyAccess**

### Steps to Setup

> Make sure all the prerequisites listed above are fulfilled before proceeding.

1. Clone this repository

```bash
git clone https://github.com/BharathMahadevP/usefulscripts-devops.git
```

2. Switch to the code directory

```bash
cd aws-account-finder/backend
```

3. Rename the sample env file to .env

```bash
mv .envsample .env
```

> After renaming the file add the Access Key ID and Secret Key to the .env file

4. Build docker image

```bash
docker build -t aws-account-finder-backend . --no-cache
```

5. Run docker container in the background

```bash
docker run -d -p 5001:5001 aws-account-finder-backend:latest
```
> Ensure that port 5001 is open and can be accessible on the server

6. Setup the necessary configurations for front end and backend on apache.
