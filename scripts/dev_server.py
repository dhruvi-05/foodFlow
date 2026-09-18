"""
Local Development API Server for WasteWise AI.
Serves all backend handlers via a simple HTTP server on port 8000.
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.fn_plan.app import plan_handler
from backend.fn_explain.app import explain_handler, ask_handler
from backend.fn_waste.app import waste_handler
from backend.fn_simulate.app import simulate_handler
from backend.fn_ingest.app import upload_url_handler


class WasteWiseHandler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        query_params = {k: v[0] for k, v in qs.items()}

        event = {"queryStringParameters": query_params}

        if path == "/api/plan":
            result = plan_handler(event)
        elif path == "/api/waste":
            result = waste_handler(event)
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return

        self._send_response(result)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        parsed = urlparse(self.path)
        path = parsed.path
        event = {"body": body}

        if path == "/api/explain":
            result = explain_handler(event)
        elif path == "/api/ask":
            result = ask_handler(event)
        elif path == "/api/simulate":
            result = simulate_handler(event)
        elif path == "/api/upload-url":
            result = upload_url_handler(event)
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return

        self._send_response(result)

    def _send_response(self, result):
        status = result.get("statusCode", 200)
        self.send_response(status)
        self._set_cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        body = result.get("body", "{}")
        self.wfile.write(body.encode() if isinstance(body, str) else json.dumps(body).encode())

    def log_message(self, format, *args):
        print(f"[API] {args[0]} {args[1]}")


def main():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), WasteWiseHandler)
    print(f"🚀 WasteWise AI Local API Server running on http://localhost:{port}")
    print(f"   Endpoints: GET /api/plan, GET /api/waste, POST /api/explain, POST /api/ask, POST /api/simulate, POST /api/upload-url")
    print(f"   Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
