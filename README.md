# Overview

Detailed decription of the backup procedure is decribed here: https://e-pilot.atlassian.net/wiki/spaces/PLAY/pages/1775337487/AWS+-+Configure+Automated+backup+for+EC2

The repository contains the code for a serverless deployment of a lambda function.
The lambda function is combination of the 2 functions deployed to automatically 

1. Create AMI backups for instances having a specific tag "BackUp".
2. Cleanup AMI backups taken by Step 1 after certain configurable retention period ("RETENTION_DAYS" environment variable).

* The tag name "BackUp" is case sensitive and should be used with the appropriate case. Example:- "BackUp"
* Environment variable `RETENTION_DAYS` (in number of days) should be configured

## Prerequisites
* You need to add a tag to the desired EC2 instance to be backed-up. You can use the following command to add tags manually.

* For one instance
```
aws ec2 create-tags --resources i-05xxxxxxxxb220fb --tags Key=BackUp,Value=""
```

* For multiple Instances
```
aws ec2 create-tags --resources i-05xxxxxxxxb220fb i-123xxxxxxxxbcdef0 --tags Key=BackUp,Value=""
```

* The tag name "BackUp" is case sensitive and should be used with the appropriate case. Example:- "BackUp"

# Deploy lambda

The below steps provide details on deploying this lambda function manually for testing purposes.
It uses aws cli for deployment.

## Deploying the function
The function can be deployed using the serverless binary.

### Serverless

#### Deploying the function
the lambda function will require a role which will have privileges to describe the EC2 instances and work with the AMI images.

Deploy command (**staging** example):
```bash
aws lambda create-function --function-name test-ec2-backup --runtime python3.7 \
--zip-file fileb://serverless-ec2-backup.zip --handler handler.handler \
--role arn:aws:iam::882235782134:role/temp-lambda-ami-backup \
--environment "Variables={RETENTION_DAYS=100}"
```
#### Update function code
```bash
aws lambda update-function-code --function-name test-ec2-backup  --zip-file fileb://serverless-ec2-backup.zip
```

# Logging

* To ship logs of this lambda function using the automatic log shipper lambda function, please execute the below command to create an event source mapping.

```
aws lambda create-event-source-mapping \
    --function-name my-function \
    --batch-size 5 \
    --event-source-arn arn:aws:logs:eu-central-1:<AWS_ACCOUNT>:log-group:/aws/lambda/ec2-backup
```

# References

* https://serverless.com/framework/docs/getting-started/

