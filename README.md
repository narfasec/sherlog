# Sherlog
<img src="https://www.clipartmax.com/png/middle/97-976283_sherlock-holmes-icon-sherlock-holmes-icon-png.png" width="150" height="150">

![](assets/sherlog.gif)
## Description
Sherlog assess the logging gap of an AWS cloud environment. It scans for resources and checks if they are logging according to security best practices. In case it detects resources that are not properly logging, sherlog gives recomendation on how to remidiate them. 

Sherlog will help you reducing the loggin gap on your AWS enviroment!

AWS services covered by Sherlog:
- S3
- DynamoDB
- Cloudfront
- RDS Databases
- ELBv2

To come:
- EC2
- Redshift

## Setup TODO
Install with pypi
```
pip install sherlog
```
Sherlog will require at least a an AWS profile with read permissions, the AWS ***SecurityAudit*** permissions are good option
## How to use

Usage:
```
sherlog --profile <profile> [options]
```

Select a set o regions:
```
sherlog --profile my_profile -r us-west-2 -r us-east-1
```

## Integrations tests
In case you want you to have an overview of what results are expectted feel free to use this TF code which provisions all resources covered by sherlog

## Credits

Octoguard team:
    - narfasec
    - 9rnt

## Collaborate
Feel free to Open PR's and contribute to sherlog!
#### Rules
- If you want to add a new feature, open a PR with a branch name starting with **feature:**
- If you want to fix an issue from *issues*, open a PR with a branch name starting with **fix-issueID:**
- If you want to fix an issue that is not included in *issues*, simply open a PR with a branch name strating with **fix-new:** and provide a detailed description of the issue found and ideally with the steps to replicate it
