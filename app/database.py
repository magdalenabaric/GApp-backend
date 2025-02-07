import boto3
import os
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",  # Lokalni DynamoDB
    region_name="us-east-1",
    # Dummy AWS kljucevi, ja imam lokalnu bazu, zamjenit ces to svojim aws kljucevima na kraju projekta
    aws_access_key_id="fakeMyKeyId",
    aws_secret_access_key="fakeSecretAccessKey"
)


def create_table(table_name, key_schema, attribute_definitions):
    existing_tables = [table.name for table in dynamodb.tables.all()]
    if table_name in existing_tables:
        print(f"Tablica {table_name} vec postoji. Preskacem kreiranje.")
        return

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                "ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )
        table.wait_until_exists()
        print(f"Tablica {table_name} uspjesno kreirana!")
    except Exception as e:
        print(f"Greska pri kreiranju tablice {table_name}: {e}")


tables = [
    {
        "name": "Users",
        "key_schema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "attribute_definitions": [{"AttributeName": "user_id", "AttributeType": "S"}],
    },
    {
        "name": "Exhibitions",
        "key_schema": [{"AttributeName": "exhibition_id", "KeyType": "HASH"}],
        "attribute_definitions": [{"AttributeName": "exhibition_id", "AttributeType": "S"}],
    },
    {
        "name": "Artworks",
        "key_schema": [
            {"AttributeName": "artwork_id", "KeyType": "HASH"},
            {"AttributeName": "exhibition_id", "KeyType": "RANGE"}
        ],
        "attribute_definitions": [
            {"AttributeName": "artwork_id", "AttributeType": "S"},
            {"AttributeName": "exhibition_id", "AttributeType": "S"}
        ],
    },
    {
        "name": "Comments",
        "key_schema": [
            {"AttributeName": "comment_id", "KeyType": "HASH"},
            {"AttributeName": "artwork_id", "KeyType": "RANGE"}
        ],
        "attribute_definitions": [
            {"AttributeName": "comment_id", "AttributeType": "S"},
            {"AttributeName": "artwork_id", "AttributeType": "S"}
        ],
    }
]

# Kreiranje tablica
for table in tables:
    create_table(
        table["name"],
        table["key_schema"],
        table["attribute_definitions"]
    )

create_table("Exhibitions", [{"AttributeName": "exhibition_id", "KeyType": "HASH"}],
             [{"AttributeName": "exhibition_id", "AttributeType": "S"}])

create_table("Artworks", [{"AttributeName": "artwork_id", "KeyType": "HASH"},
                          {"AttributeName": "exhibition_id", "KeyType": "RANGE"}],
             [{"AttributeName": "artwork_id", "AttributeType": "S"},
              {"AttributeName": "exhibition_id", "AttributeType": "S"}])

create_table("Comments", [{"AttributeName": "comment_id", "KeyType": "HASH"},
                          {"AttributeName": "artwork_id", "KeyType": "RANGE"}],
             [{"AttributeName": "comment_id", "AttributeType": "S"},
              {"AttributeName": "artwork_id", "AttributeType": "S"}])
