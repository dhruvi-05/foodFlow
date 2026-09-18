"""
DynamoDB single-table helper functions and key builders for WasteWise AI.
"""

import os
import boto3
from typing import Dict, Any, List, Optional

TABLE_NAME = os.environ.get("TABLE_NAME", "WasteWiseTable")


def get_dynamodb_resource():
    return boto3.resource("dynamodb")


def get_table():
    return get_dynamodb_resource().Table(TABLE_NAME)


# Key Builders
def rest_pk(restaurant_id: str = "R001") -> str:
    return f"REST#{restaurant_id}"


def dish_sk(dish_id: str) -> str:
    return f"DISH#{dish_id}"


def sale_sk(date_str: str, dish_id: str) -> str:
    return f"SALE#{date_str}#{dish_id}"


def inv_sk(date_str: str) -> str:
    return f"INV#{date_str}"


def fcst_sk(date_str: str, dish_id: str) -> str:
    return f"FCST#{date_str}#{dish_id}"


def job_sk(job_id: str) -> str:
    return f"JOB#{job_id}"


def waste_gsi1pk(restaurant_id: str = "R001") -> str:
    return f"REST#{restaurant_id}#WASTE"


def waste_gsi1sk(waste_reason: str, date_str: str) -> str:
    return f"{waste_reason}#{date_str}"
