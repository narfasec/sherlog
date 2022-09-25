# Sherlog
<img src="https://www.clipartmax.com/png/middle/286-2860475_sherlock-holmes-silhouette-chess-knight-icon-png.png" width="250" height="250">

## Description
Inspects resources logging status and gives recomendations according to security best practices

Services covered by this tool:
- AWS ELB
- API Gateway
- S3 Buckets
- RDS Databases
- EC2 instances
- Redshift Databases

## Setup
Create a role in your environment with the below (example) trust relationship policy and assign the AWS ***SecurityAudit*** permissions

Example:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Principal": {
                "AWS": "YOUR_ACCOUNT_id"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "YOUR_EXTERNAL_ID"
                }
            }
        }
    ]
}
```

Set the environment variables required. Follow next section
## Env variables description

| Variable | Description |
|----------|-------------|
| LOG_LEVEL | Log level required by the app |
| ROLE_NAME | The role name for the app to assume. Must have read only permissions to the services covered by the tool |
| ACCOUNTS_CONFIGURATION | A list of dicts (passed as string) of the accounts id and external ids used by to assume the role (consider passing it with a secret manager tool). When no external Id is configured in the assume role do not pass it. Example: [{'accountId':'18976838763','externalId':'lkjdalkj/9871lklazdlkKLJldn'},{'accountId':'198719871379'}] |
| DB_URL | The Arangodb url. Example http://localhost:8529 |
| DB_NAME | ArangoDB name |
| DB_USERNAME | Arangodb user name |
| DB_PASSWORD | Arangodb password (consider passing it with a secret manager tool) |