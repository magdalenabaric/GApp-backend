import sys
import boto3

# Postavljamo encoding na UTF-8
sys.stdout.reconfigure(encoding='utf-8')

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="us-east-1",
    aws_access_key_id="fakeMyKeyId",
    aws_secret_access_key="fakeSecretAccessKey"
)

tables = list(dynamodb.tables.all())
print("Postojeće tablice:", [table.name for table in tables])
