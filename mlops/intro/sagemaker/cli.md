# Install SageMaker using AWS CLI

### Get the Default VPC ID

```
aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" \
  --output text \
  --region <REGION>
```

### List Subnets Under the Default VPC

```
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=<DEFAULT_VPC_ID>" \
  --query "Subnets[].SubnetId" \
  --output text \
  --region <REGION>
```

### Create an Execution Role for SageMaker Domain

Create a simple trust policy

Save as trust.json:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "sagemaker.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create the role

```
aws iam create-role \
  --role-name SageMakerDomainExecutionRole \
  --assume-role-policy-document file://trust.json
```

Attach a basic policy (beginner friendly)

```
aws iam attach-role-policy \
  --role-name SageMakerDomainExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
```

Save the role ARN from:

`aws iam get-role --role-name SageMakerDomainExecutionRole --query "Role.Arn" --output text`

### Create the SageMaker Domain (Using Default VPC)

This is the core step.

```
aws sagemaker create-domain \
  --domain-name my-sagemaker-domain \
  --auth-mode IAM \
  --vpc-id <DEFAULT_VPC_ID> \
  --subnet-ids <SUBNET1> <SUBNET2> \
  --app-network-access-type VpcOnly \
  --default-user-settings "{
      \"ExecutionRole\": \"<ROLE_ARN>\"
   }" \
  --region <REGION>
```

This returns a DomainId. If you lose it, list domains:

`aws sagemaker list-domains --region <REGION>`

### Create a SageMaker UserProfile + Tag It

ABAC depends on tags.

```
aws sagemaker create-user-profile \
  --domain-id <DOMAIN_ID> \
  --user-profile-name alice-profile \
  --tags Key=studiouserid,Value=alice123 \
  --region <REGION>
```

### Create the IAM User and Tag the User

The IAM user must have the same tag for ABAC matching.

```
aws iam create-user --user-name alice-iam-user
```

Add ABAC tag

```
aws iam tag-user \
  --user-name alice-iam-user \
  --tags Key=studiouserid,Value=alice123
```

### Create the ABAC Policy

This policy enforces two things:

The IAM user can only generate a presigned URL for a user profile whose tag matches their own (studiouserid).

The IAM user can view the domain and user profile in the SageMaker console.

Save this as sagemaker-abac.json:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowConsoleListAndDescribe",
      "Effect": "Allow",
      "Action": [
        "sagemaker:ListDomains",
        "sagemaker:ListUserProfiles",
        "sagemaker:ListApps",
        "sagemaker:DescribeDomain",
        "sagemaker:DescribeUserProfile",
        "sagemaker:ListTags"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowPresignedUrlWhenTagMatches",
      "Effect": "Allow",
      "Action": [
        "sagemaker:CreatePresignedDomainUrl"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "sagemaker:ResourceTag/studiouserid": "${aws:PrincipalTag/studiouserid}"
        }
      }
    }
  ]
}
```

### Create the IAM policy

```
aws iam create-policy \
  --policy-name SageMaker-Studio-ABAC \
  --policy-document file://sagemaker-abac.json
```

### Attach the Policy to the IAM User

```
aws iam attach-user-policy \
  --user-name alice-iam-user \
  --policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/SageMaker-Studio-ABAC
```

### How the IAM User Opens SageMaker Studio

There are two ways now:

Using the SageMaker Console (now works due to list permissions)

- IAM user signs in → goes to:
- Amazon SageMaker → Studio → Domains
- They can now see: The domain -> The user profile

Using a Presigned URL (ABAC-restricted)

The user (or admin) runs:

```
aws sagemaker create-presigned-domain-url \
  --domain-id <DOMAIN_ID> \
  --user-profile-name alice-profile \
  --session-expiration-duration-in-seconds 3600 \
  --region <REGION>
```

This returns a URL that opens SageMaker Studio only for this UserProfile.

If an IAM user tries to open another user’s profile → access denied because the tags won't match.


# Create and Save Models to SageMaker

### Create an S3 bucket

`aws s3 mb s3://my-sagemaker-demo-bucket-abhishek`

### Create IAM Execution Role for SageMaker

Create trust policy - trust.json

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "sagemaker.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Create the role

```
aws iam create-role \
  --role-name SageMakerDemoExecutionRole \
  --assume-role-policy-document file://trust.json
```

Attach permissions

```
aws iam attach-role-policy \
  --role-name SageMakerDemoExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
```

```
aws iam attach-role-policy \
  --role-name SageMakerDemoExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Find default VPC + default subnets

Get Default VPC

```
aws ec2 describe-vpcs --filters Name=isDefault,Values=true \
  --query "Vpcs[0].VpcId" --output text
```

Get subnets

```
aws ec2 describe-subnets --filters Name=vpc-id,Values=<VPC-ID> \
  --query "Subnets[*].SubnetId" --output text
```

Pick 2 subnets.

### Create SageMaker Domain (Studio)

```
aws sagemaker create-domain \
  --domain-name demo-domain \
  --auth-mode IAM \
  --default-user-settings "ExecutionRole=arn:aws:iam::<ACCOUNT-ID>:role/SageMakerDemoExecutionRole" \
  --vpc-id <VPC-ID> \
  --subnet-ids "<SUBNET-1>" "<SUBNET-2>"
```

Note the returned DomainId.

### Create User Profile

```
aws sagemaker create-user-profile \
  --domain-id <DOMAIN-ID> \
  --user-profile-name demo-user
```

### Open SageMaker Studio

Go to:

AWS Console → SageMaker → Domains → demo-domain → Launch app → Studio

Select demo-user.

A JupyterLab interface will open.

### Inside Studio: Train a simple model & Push to S3

Open a Python 3 Notebook.

Now run the following code.

### Import libraries

```
import boto3
import joblib
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
import os
```

#### Train a tiny ML model

```
iris = load_iris()
X, y = iris.data, iris.target

model = DecisionTreeClassifier()
model.fit(X, y)

joblib.dump(model, "iris-model.pkl")

print("Model saved as iris-model.pkl")
```

#### Upload model to S3

```
import boto3

s3 = boto3.client("s3")
bucket = "my-sagemaker-demo-bucket-abhishek"

s3.upload_file("iris-model.pkl", bucket, "model-artifacts/iris-model.pkl")

print("Uploaded to S3:", f"s3://{bucket}/model-artifacts/iris-model.pkl")
```

### Verify upload from CLI

`aws s3 ls s3://my-sagemaker-demo-bucket-abhishek/model-artifacts/`

You will see:

`iris-model.pkl`


# Deploy and Save Model for Inference using AWS SageMaker

### Create Inference Script (UI)

Inside SageMaker Studio:

Click File → New → Text File

Name it: inference.py

Paste this:

```
import joblib
import os
import json

def model_fn(model_dir):
    model = joblib.load(os.path.join(model_dir, "iris-model.pkl"))
    return model

def input_fn(request_body, request_content_type):
    data = json.loads(request_body)
    return data["instances"]

def predict_fn(input_data, model):
    return model.predict(input_data)

def output_fn(prediction, content_type):
    return json.dumps({"predictions": prediction.tolist()})
```

Save the file.

### Package Model for SageMaker

SageMaker does NOT deploy loose files. It expects a tar.gz file.

Run this in the notebook:

```
import tarfile

with tarfile.open("model.tar.gz", "w:gz") as tar:
    tar.add("iris-model.pkl")
    tar.add("inference.py")

print("model.tar.gz created")
```

### Upload model.tar.gz to S3

```
s3.upload_file(
    "model.tar.gz",
    bucket_name,
    "model-artifacts/model.tar.gz"
)

print("Packaged model uploaded to S3")
```

Now SageMaker can deploy this model.

### Create Model

Go to SageMaker → Models

Click Create model

Model name: `iris-demo-model`

Container settings

Framework: `Scikit-learn`

Version: `1.2`

Model data location: [Change accordingly]

`s3://my-sagemaker-demo-bucket-abhishek/model-artifacts/model.tar.gz`

IAM role

Select your SageMaker execution role

Click Create model

### Create Endpoint Configuration (UI)

Go to Inference → Endpoint configurations

Click Create endpoint configuration

Name: `iris-endpoint-config`

Production variant

Model: `iris-demo-model`

Instance type: `ml.t2.medium`

Initial instance count: `1`

Click Create

### Create Endpoint 

Go to Inference → Endpoints

Click Create endpoint

Endpoint name: `iris-demo-endpoint`

Select endpoint configuration: `iris-endpoint-config`

Click Create endpoint

⏳ Wait ~5–7 minutes

Status should become InService

### Test Endpoint (UI)

Open Endpoints

Click `iris-demo-endpoint`

Click Test inference

Input:

```
{
  "instances": [[5.1, 3.5, 1.4, 0.2]]
}
```

Click Test

You’ll see:

```
{"predictions":[0]}
```

🎉 Your model is live.