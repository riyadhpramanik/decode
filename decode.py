from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import base64
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # This handles the "Pre-flight" request browsers send for security
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        try:
            query = urlparse(self.path).query
            params = parse_qs(query)
            token = params.get('token', [None])[0]

            if not token:
                self.send_error_response(400, "Token parameter is required")
                return

            parts = token.split('.')
            if len(parts) != 3:
                self.send_error_response(400, "Invalid JWT format")
                return

            def decode_base64(data):
                data += '=' * (4 - len(data) % 4)
                return json.loads(base64.urlsafe_b64decode(data).decode('utf-8'))

            payload = decode_base64(parts[1])

            if 'exp' in payload:
                payload['exp_date'] = datetime.utcfromtimestamp(payload['exp']).strftime('%Y-%m-%d %H:%M:%S')
            if 'lock_region_time' in payload:
                payload['lock_region_date'] = datetime.utcfromtimestamp(payload['lock_region_time']).strftime('%Y-%m-%d %H:%M:%S')

            # Send Success Response with CORS Headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # ALLOWS YOUR SITE
            self.end_headers()
            self.wfile.write(json.dumps(payload, indent=2).encode())

        except Exception as e:
            self.send_error_response(400, str(e))

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())