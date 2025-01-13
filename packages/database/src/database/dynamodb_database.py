import boto3
from botocore.exceptions import BotoCoreError, ClientError
from boto3.dynamodb.types import TypeSerializer
from database.interface import NoSqlDb
import time
from pydantic import BaseModel, Field
from typing import Optional, List
class DynamoDBDatabase(NoSqlDb):
    """Implementation of NoSqlDb using AWS DynamoDB."""

    def __init__(
        self,
        table_prefix: str = "",
        region_name: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
    ):
        """Initialize DynamoDB client with optional AWS credentials."""
        
        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        self.table_prefix = table_prefix
        self.serializer = TypeSerializer()

        
    def _get_table(self, table: str):
        """Helper function to get a DynamoDB table."""
        return self.dynamodb.Table(f"{self.table_prefix}{table}")

    def _serialize_item(self, item: dict) -> dict:
        """
        Convert Pydantic model (or dict) into DynamoDB's expected format using TypeSerializer.
        """
        serialized_item = {}
        for k, v in item.items():
            if k == "id":  # Ensure id is always a string
                serialized_item[k] = self.serializer.serialize(str(v))  # Convert id explicitly to str
            else:
                serialized_item[k] = self.serializer.serialize(v)
        return serialized_item

    def insert_item(self, table: str, key: str, item: BaseModel) -> dict:
        """Insert a Pydantic model into DynamoDB using TypeSerializer."""
        try:

            print(f"Inserting key {key} item: {item}")

            table_ref = self._get_table(table)

            if isinstance(item, BaseModel):
                item = item.dict()  # Convert Pydantic model to dict

            item["id"] = str(key)  # Ensure 'id' is explicitly a string

            # serialized_item = self._serialize_item(item)  # Convert to DynamoDB format
            serialized_item = item 

            print(f"Serialized item: {serialized_item}")
            table_ref.put_item(Item=serialized_item)
            return item
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"DynamoDB insert failed: {e}")
        

    def get_item(self, table: str, key: str) -> dict:
        """Retrieve an item by key from DynamoDB."""
        print(f"Retrieving item with key {key} from table {table}")
        try:
            table_ref = self._get_table(table)
            response = table_ref.get_item(Key={"id": key})
            return response.get("Item", {})
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"DynamoDB get failed: {e}")

    def get_all_items(self, table: str) -> list:
        """Retrieve all items from a DynamoDB table (scan operation)."""
        try:
            table_ref = self._get_table(table)
            response = table_ref.scan()
            return response.get("Items", [])
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"DynamoDB scan failed: {e}")

    def update_item(self, table: str, key: str, updates: dict) -> dict:
        """Update an item in DynamoDB."""
        try:
            table_ref = self._get_table(table)

            # Remove 'id' from updates to prevent modification errors
            updates = {k: v for k, v in updates.items() if k != "id"}

            if not updates:
                raise ValueError("No valid fields to update. 'id' cannot be modified.")

            # Convert updates dictionary into an update expression
            update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in updates.keys())
            expression_attr_values = {f":{k}": v for k, v in updates.items()}
            expression_attr_names = {f"#{k}": k for k in updates.keys()}

            response = table_ref.update_item(
                Key={"id": key},  # Ensure 'id' is used only for lookup
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attr_values,
                ExpressionAttributeNames=expression_attr_names,
                ReturnValues="ALL_NEW",
            )
            return response.get("Attributes", {})
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"DynamoDB update failed: {e}")

    def delete_item(self, table: str, key: str) -> None:
        """Delete an item from DynamoDB."""
        try:
            table_ref = self._get_table(table)
            table_ref.delete_item(Key={"id": key})
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"DynamoDB delete failed: {e}")
