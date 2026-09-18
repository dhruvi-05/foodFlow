"""
Standard HTTP API responses and error envelopes for WasteWise AI.
"""

import json
from typing import Dict, Any, Optional

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Cache-Control": "public, max-age=60"
}


def json_response(status_code: int, body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Generates an HTTP API Gateway response dictionary with standard headers."""
    merged_headers = dict(CORS_HEADERS)
    if headers:
        merged_headers.update(headers)
    
    return {
        "statusCode": status_code,
        "headers": merged_headers,
        "body": json.dumps(body) if not isinstance(body, str) else body
    }


def error_response(code: str, message: str, status_code: int = 400, retryable: bool = False) -> Dict[str, Any]:
    """Generates a structured error response according to Section 10.1 of the spec."""
    payload = {
        "error": {
            "code": code,
            "message": message,
            "retryable": retryable
        }
    }
    return json_response(status_code, payload)
