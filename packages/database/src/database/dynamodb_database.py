import boto3
from botocore.exceptions import BotoCoreError, ClientError
from database.interface import NoSqlDb

class DynamoDBDatabase(NoSqlDb):
    """Implementation of NoSqlDb using AWS DynamoDB."""

    def __init__(self, table_prefix: str = "", region_name: str = "us-east-1"):
        """Initialize DynamoDB client and set table prefix (if any)."""
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table_prefix = table_prefix

    def _get_table(self, table: str):
        """Helper function to get a DynamoDB table."""
        return self.dynamodb.Table(f"{self.table_prefix}{table}")

    def insert_item(self, table: str, key: str, item: dict) -> dict:
        """Insert an item into DynamoDB."""
        try:
            item["id"] = key  # Ensuring the key is in the item
            table_ref = self._get_table(table)
            table_ref.put_item(Item=item)
            return item
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"DynamoDB insert failed: {e}")

    def get_item(self, table: str, key: str) -> dict:
        """Retrieve an item by key from DynamoDB."""
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

            # Convert updates dictionary into an update expression
            update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in updates.keys())
            expression_attr_values = {f":{k}": v for k, v in updates.items()}
            expression_attr_names = {f"#{k}": k for k in updates.keys()}

            response = table_ref.update_item(
                Key={"id": key},
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
