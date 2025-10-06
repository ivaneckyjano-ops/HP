#!/usr/bin/env python3
"""Simple token proxy

Provides a tiny HTTP API to serve current access token to local services.
GET /token -> {"access_token": "...", "expires_at": 1234567890}

This service reads the same TOKENS_FILE used by the token daemon.
"""
import os
import json
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

TOKENS_FILE = os.getenv("TOKENS_FILE", "/data/tokens_min.json")
HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PORT = int(os.getenv("PROXY_PORT", "8080"))


def _jwt_exp(token: str):
    try:
        if token.count('.') < 2:
            return None
        header, payload, sig = token.split('.', 2)
        # base64url decode payload
        rem = len(payload) % 4
        if rem:
            payload += '=' * (4 - rem)
        data = json.loads(base64.urlsafe_b64decode(payload.encode('utf-8')).decode('utf-8'))
        exp = data.get('exp')
        if isinstance(exp, str) and exp.isdigit():
            return int(exp)
        if isinstance(exp, (int, float)):
            return int(exp)
    except Exception:
        return None
    return None


def load_tokens():
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        # Friendly redirect from root to /token
        if parsed.path == "/":
            self.send_response(302)
            self.send_header("Location", "/token")
            self.end_headers()
            return
        # Basic healthcheck endpoint
        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        if parsed.path != "/token":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return
        tokens = load_tokens()
        if not tokens:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"{}")
            return
        access_token = tokens.get("access_token")
        expires_at = tokens.get("expires_at")
        if not expires_at and access_token:
            # Try derive from JWT exp
            derived = _jwt_exp(access_token)
            if derived:
                expires_at = derived
        out = {"access_token": access_token, "expires_at": expires_at}
        body = json.dumps(out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args, **kwargs):
        return


def main():
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Token proxy listening on {HOST}:{PORT}, serving tokens from {TOKENS_FILE}")
    server.serve_forever()


if __name__ == "__main__":
    main()
