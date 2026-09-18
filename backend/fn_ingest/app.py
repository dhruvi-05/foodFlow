"""
S3 Presigned Upload & Data Ingestion Handler for WasteWise AI (POST /api/upload-url).
Validates canonical CSV schema and writes records to DynamoDB single table.
"""

import os
import sys
import json
import uuid
import boto3
import pandas as pd
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.common.responses import json_response, error_response
from backend.common.ddb import get_table, rest_pk, sale_sk, waste_gsi1pk, waste_gsi1sk

CANONICAL_COLUMNS = [
    "date", "restaurant_id", "dish_id", "dish_name", "category",
    "price", "promotion", "day_of_week", "holiday", "temperature",
    "rainfall", "units_prepared", "units_sold", "units_wasted",
    "waste_reason", "opening_inventory", "closing_inventory"
]


def upload_url_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """POST /api/upload-url - generates presigned S3 upload URL."""
    try:
        bucket_name = os.environ.get("DATA_BUCKET", "wastewise-data-bucket")
        file_id = str(uuid.uuid4())
        s3_key = f"uploads/R001/{file_id}.csv"

        try:
            s3_client = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
            presigned_url = s3_client.generate_presigned_url(
                "put_object",
                Params={"Bucket": bucket_name, "Key": s3_key, "ContentType": "text/csv"},
                ExpiresIn=300
            )
        except Exception:
            presigned_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

        return json_response(200, {
            "upload_url": presigned_url,
            "file_id": file_id,
            "s3_key": s3_key,
            "expires_in_seconds": 300
        })

    except Exception as e:
        return error_response("INTERNAL", f"Server error: {str(e)}", status_code=500)


def s3_event_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """S3 object created trigger parser & DynamoDB batch writer."""
    try:
        table = get_table()
        s3_client = boto3.client("s3")

        records_processed = 0
        records_rejected = 0

        for record in event.get("Records", []):
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]

            obj = s3_client.get_object(Bucket=bucket, Key=key)
            df = pd.read_csv(obj["Body"])

            # Validate canonical columns
            missing = [c for c in CANONICAL_COLUMNS if c not in df.columns]
            if missing:
                print(f"REJECTED: Missing canonical columns: {missing}")
                records_rejected += len(df)
                continue

            with table.batch_writer() as batch:
                for _, row in df.iterrows():
                    d_id = str(row["dish_id"])
                    dt_str = str(row["date"])
                    w_reason = str(row.get("waste_reason", "none"))

                    item = {
                        "PK": rest_pk(str(row.get("restaurant_id", "R001"))),
                        "SK": sale_sk(dt_str, d_id),
                        "dish_name": str(row["dish_name"]),
                        "category": str(row["category"]),
                        "price": float(row["price"]),
                        "units_prepared": int(row["units_prepared"]),
                        "units_sold": int(row["units_sold"]),
                        "units_wasted": int(row["units_wasted"]),
                        "waste_reason": w_reason,
                        "opening_inventory": int(row.get("opening_inventory", 0)),
                        "closing_inventory": int(row.get("closing_inventory", 0)),
                        "GSI1PK": waste_gsi1pk(str(row.get("restaurant_id", "R001"))),
                        "GSI1SK": waste_gsi1sk(w_reason, dt_str)
                    }
                    batch.put_item(Item=item)
                    records_processed += 1

        return json_response(200, {
            "status": "SUCCESS",
            "records_processed": records_processed,
            "records_rejected": records_rejected
        })

    except Exception as e:
        return error_response("INTERNAL", f"Ingestion error: {str(e)}", status_code=500)
