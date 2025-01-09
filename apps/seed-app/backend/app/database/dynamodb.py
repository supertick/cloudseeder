import boto3
from .interface import NoSqlDb

class DynamoDBDatabase(NoSqlDb):
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.client = boto3.resource("dynamodb").Table(table_name)

    def insert_item(self, item: dict) -> dict:
        self.client.put_item(Item=item)
        return item

    def get_item(self, key: str) -> dict:
        response = self.client.get_item(Key={"uuid": key})  # Ensure 'uuid' is the key
        return response.get("Item", {})

    def update_item(self, key: str, updates: dict) -> dict:
        update_expression = "SET " + ", ".join(f"{k}=:{k}" for k in updates)
        expression_values = {f":{k}": v for k, v in updates.items()}
        self.client.update_item(
            Key={"uuid": key},  # Ensure 'uuid' is the key
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
        )
        return self.get_item(key)

    def delete_item(self, key: str) -> None:
        self.client.delete_item(Key={"uuid": key})
