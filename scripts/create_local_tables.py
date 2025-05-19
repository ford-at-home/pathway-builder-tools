import os

import boto3
from botocore.exceptions import ClientError

# Use environment variable or default to local DynamoDB
DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

# Table definitions
TABLES = [
    {
        "TableName": "Subscriptions",
        "KeySchema": [
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    },
    {
        "TableName": "Products",
        "KeySchema": [
            {"AttributeName": "product_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "product_id", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    },
    {
        "TableName": "Goals",
        "KeySchema": [
            {"AttributeName": "goal_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "goal_id", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    },
]


def create_table(dynamodb, table_def):
    table_name = table_def["TableName"]
    try:
        existing = dynamodb.Table(table_name)
        existing.load()
        print(f"Table '{table_name}' already exists. Skipping.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"Creating table '{table_name}'...")
            dynamodb.create_table(**table_def)
            print(f"Table '{table_name}' created.")
        else:
            print(f"Error checking/creating table '{table_name}': {e}")
            raise


def main():
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=DYNAMODB_ENDPOINT,
        region_name=REGION,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "fakeMyKeyId"),
        aws_secret_access_key=os.environ.get(
            "AWS_SECRET_ACCESS_KEY", "fakeSecretAccessKey"
        ),
    )
    for table_def in TABLES:
        create_table(dynamodb, table_def)


if __name__ == "__main__":
    main()
