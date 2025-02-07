import json
import logging
import re
from typing import Dict, List, Any, Union
import boto3
from botocore.exceptions import ClientError

from .interface import NoSqlDb

logger = logging.getLogger(__name__)


class S3Database(NoSqlDb):
    def __init__(self, config: Dict[str, str]):
        """
        Initialize the S3Database implementation.
        
        Expected configuration keys:
          - bucket_name: The name of the S3 bucket to use.
          - region_name (optional): AWS region.
          - aws_access_key_id (optional): AWS access key ID.
          - aws_secret_access_key (optional): AWS secret access key.
        """
        self.config = config
        self.bucket_name = config.get("bucket_name")
        if not self.bucket_name:
            raise ValueError("S3Database requires a 'bucket_name' in the config.")

        # Optionally pass credentials or region settings if provided in config.
        region_name = config.get("region_name")
        aws_access_key_id = config.get("aws_access_key_id")
        aws_secret_access_key = config.get("aws_secret_access_key")

        if aws_access_key_id and aws_secret_access_key:
            self.s3 = boto3.resource(
                "s3",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        else:
            self.s3 = boto3.resource("s3", region_name=region_name) if region_name else boto3.resource("s3")

        self.bucket = self.s3.Bucket(self.bucket_name)
        logger.info(f"S3Database initialized with bucket: {self.bucket_name}")

    def _get_s3_key(self, table: str, key: str) -> str:
        """Construct the S3 object key for the given table and key."""
        return f"{table}/{key}"

    def insert_item(self, table: str, key: str, item: dict) -> dict:
        """Insert an item into the specified table (S3 prefix)."""
        logger.info(f"Inserting item into table '{table}' with key '{key}': {item}")
        # Ensure the key is included in the item
        # item["id"] = key - bad idea
        s3_key = self._get_s3_key(table, key)
        item_json = json.dumps(item)
        try:
            self.bucket.put_object(Key=s3_key, Body=item_json)
            logger.info(f"Item inserted successfully at S3 key: {s3_key}")
        except ClientError as e:
            logger.exception("Failed to insert item into S3")
            raise e
        return item

    def get_item(self, table: str, key: str) -> dict:
        """Retrieve an item by key from the specified table (S3 prefix)."""
        logger.info(f"Retrieving item from table '{table}' with key: {key}")
        s3_key = self._get_s3_key(table, key)
        try:
            obj = self.s3.Object(self.bucket_name, s3_key)
            response = obj.get()
            data = response["Body"].read().decode("utf-8")
            item = json.loads(data)
            logger.info(f"Item retrieved: {item}")
            return item
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "NoSuchKey":
                logger.warning(f"Item with key '{key}' not found in table '{table}'.")
                return {}
            else:
                logger.exception("Error retrieving item from S3")
                raise e
            
    def get_binary_item(self, table: str, key: str) -> bytes:
        s3_key = self._get_s3_key(table, key)
        logger.info(f"Retrieving binary item from bucket with key: {s3_key}")
        try:
            obj = self.s3.Object(self.bucket_name, s3_key)
            response = obj.get()

            body = response["Body"].read()

            logger.info("Binary or non-JSON data retrieved.")
            return body

        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "NoSuchKey":
                logger.warning(f"Item with key '{key}' not found in table '{table}'.")
                return {}
            else:
                logger.exception("Error retrieving item from S3")
                raise e            

    def get_all_items(self, table: str) -> list:
        """Retrieve all items from the specified table (S3 prefix)."""
        logger.info(f"Retrieving all items from table '{table}'")
        prefix = f"{table}/"
        items = []
        try:
            for obj_summary in self.bucket.objects.filter(Prefix=prefix):
                obj = self.s3.Object(self.bucket_name, obj_summary.key)
                response = obj.get()
                data = response["Body"].read().decode("utf-8")
                item = json.loads(data)
                items.append(item)
            logger.info(f"Total items retrieved from '{table}': {len(items)}")
            return items
        except ClientError as e:
            logger.exception("Error retrieving all items from S3")
            raise e

    def update_item(self, table: str, key: str, updates: dict) -> dict:
        """
        Update an item in the specified table (S3 prefix) by merging the updates.
        If the item doesn't exist, a warning is logged.
        """
        logger.info(f"Updating item in table '{table}' with key '{key}' using updates: {updates}")
        existing_item = self.get_item(table, key)
        if not existing_item:
            logger.warning(f"Item with key '{key}' not found in table '{table}', update skipped.")
            return {}
        existing_item.update(updates)
        s3_key = self._get_s3_key(table, key)
        try:
            self.bucket.put_object(Key=s3_key, Body=json.dumps(existing_item))
            logger.info(f"Item updated successfully: {existing_item}")
        except ClientError as e:
            logger.exception("Failed to update item in S3")
            raise e
        return existing_item

    def delete_item(self, table: str, key: str) -> None:
        """Delete an item from the specified table (S3 prefix)."""
        logger.info(f"Deleting item from table '{table}' with key: {key}")
        s3_key = self._get_s3_key(table, key)
        try:
            obj = self.s3.Object(self.bucket_name, s3_key)
            obj.delete()
            logger.info(f"Item with key '{key}' deleted from table '{table}'")
        except ClientError as e:
            logger.exception("Failed to delete item from S3")
            raise e

    def search_by_key_part(self, table: str, key_part: str, regex: bool = False) -> List[Dict[str, Any]]:
        """
        Search for items in the specified table (S3 prefix) whose keys contain or match a part of the given key.
        
        :param table: The table (prefix) to search in.
        :param key_part: The key part to search for.
        :param regex: If True, treat key_part as a regular expression; otherwise, do a prefix match.
        :return: A list of matching items.
        """
        logger.info(f"Searching in table '{table}' for keys matching: {key_part} (regex={regex})")
        items = self.get_all_items(table)
        if regex:
            pattern = re.compile(key_part)
            matching_items = [item for item in items if "id" in item and pattern.search(item["id"])]
        else:
            matching_items = [item for item in items if "id" in item and item["id"].startswith(key_part)]
        logger.info(f"Found {len(matching_items)} matching items in table '{table}'")
        return matching_items
