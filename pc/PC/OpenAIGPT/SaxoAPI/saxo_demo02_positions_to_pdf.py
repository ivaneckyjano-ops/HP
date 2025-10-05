# (file starts here)
import base64
import hashlib
import json
import os
import time
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    HAVE_REPORTLAB = True
except Exception:  # pragma: no cover - missing optional dependency
    HAVE_REPORTLAB = False


# ------- Config -------
CLIENT_ID = "2d7a66918b594af5bc2ac830a3b79d2c"  # váš SIM AppKey
CLIENT_SECRET = os.getenv("SAXO_CLIENT_SECRET", "").strip()  # nechajte prázdne, ak nemáte secret
ENV = "sim"  # sim | live
REDIRECT_URI = "http://localhost:8765/callback"  # musí bitovo sedieť s registráciou v Saxo app
SCOPES = "openid offline_access read trade"

TOKEN_STORE = "tokens.json"
OUT_PDF = "positions.pdf"
OUT_RAW = "positions_raw.json"

if ENV == "live":
    AUTH_BASE = "https://live.logonvalidation.net"
    GATEWAY_BASE = "https://gateway.saxobank.com/openapi"
else:
    AUTH_BASE = "https://sim.logonvalidation.net"
    GATEWAY_BASE = "https://gateway.saxobank.com/sim/openapi"

AUTH_URL = f"{AUTH_BASE}/authorize"
TOKEN_URL = f"{AUTH_BASE}/token"


# ------- Helpers -------
def _now() -> int:
    return int(time.time())


def save_tokens(tokens: dict):
    # atomic write + restrict permissions
    tmp = TOKEN_STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)
    try:
        os.replace(tmp, TOKEN_STORE)
    except Exception:
        # fallback: try remove and rename
        if os.path.exists(TOKEN_STORE):
            os.remove(TOKEN_STORE)
        os.replace(tmp, TOKEN_STORE)
    try:
        os.chmod(TOKEN_STORE, 0o600)
    except Exception:
        # non-fatal on platforms that don't support chmod
        pass


def load_tokens():
    if not os.path.exists(TOKEN_STORE):
        return None
    with open(TOKEN_STORE, "r", encoding="utf-8") as f:
        return json.load(f)


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def pkce_pair():
    # verifier 43–128 znakov; ~40 bajtov → ~54 znakov
    verifier = b64url(os.urandom(40))
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge


# ------- Local HTTP server for OAuth callback -------
class OAuthHandler(BaseHTTPRequestHandler):
    server_version = "SaxoOAuth/1.0"
    query_params = {}

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != urlparse(REDIRECT_URI).path:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return
        params = parse_qs(parsed.query)
        OAuthHandler.query_params = {k: v[0] for k, v in params.items()}
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"You can close this window and return to the script.")
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, format, *args):
        # ticho
        pass


def start_callback_server():
    OAuthHandler.query_params = {}
    parsed = urlparse(REDIRECT_URI)
    host = parsed.hostname or "localhost"
    port = parsed.port or 80
    try:
        httpd = HTTPServer((host, port), OAuthHandler)
    except OSError:
        httpd = HTTPServer(("", port), OAuthHandler)
    print(f"Callback server listening on {host or '0.0.0.0'}:{port} path={urlparse(REDIRECT_URI).path}")
    httpd.serve_forever()
    return OAuthHandler.query_params


# ------- OAuth (Authorization Code + PKCE alebo client_secret) -------
def get_tokens_interactive():
    if not CLIENT_ID:
        raise RuntimeError("Missing CLIENT_ID.")

    use_secret = bool(CLIENT_SECRET)
    verifier = None
    challenge = None
    if not use_secret:
        verifier, challenge = pkce_pair()

    state = b64url(os.urandom(16))

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
    }
    if not use_secret:
        params["code_challenge"] = challenge
        params["code_challenge_method"] = "S256"

    url = f"{AUTH_URL}?{urlencode(params)}"

    threading.Thread(target=start_callback_server, daemon=True).start()

    print(f"Opening browser (ENV={ENV}):\n{url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    while not OAuthHandler.query_params:
        time.sleep(0.2)

    cb = OAuthHandler.query_params
    if "error" in cb:
        raise RuntimeError(f"OAuth error: {cb.get('error_description') or cb['error']}")
    if "code" not in cb:
        raise RuntimeError(f"OAuth callback without code: {cb}")
    if cb.get("state") != state:
        raise RuntimeError("State mismatch, aborting.")

    token_data = {
        "grant_type": "authorization_code",
        "code": cb["code"],
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
    }
    if use_secret:
        token_data["client_secret"] = CLIENT_SECRET
    else:
        token_data["code_verifier"] = verifier

    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    r = requests.post(TOKEN_URL, data=token_data, headers=headers, timeout=30)
    print("Token response status:", r.status_code)
    print("Token response body:", r.text)
    print("Token response headers:", dict(r.headers))
    if r.status_code != 200:
        raise RuntimeError(f"Token exchange failed: {r.status_code}")

    tokens = r.json()
    tokens["expires_at"] = _now() + int(tokens.get("expires_in", 1800)) - 30
    save_tokens(tokens)
    return tokens


def refresh_tokens(tokens):
    if not tokens or "refresh_token" not in tokens:
        return None
    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": CLIENT_ID,
    }
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    r = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"Refresh failed: {r.status_code} {r.text}")
        return None
    new_tokens = r.json()
    new_tokens["refresh_token"] = new_tokens.get("refresh_token", tokens["refresh_token"])
    new_tokens["expires_at"] = _now() + int(new_tokens.get("expires_in", 1800)) - 30
    save_tokens(new_tokens)
    return new_tokens


def get_valid_tokens():
    tokens = load_tokens()
    if tokens and tokens.get("expires_at", 0) > _now():
        return tokens
    if tokens:
        refreshed = refresh_tokens(tokens)
        if refreshed:
            return refreshed
    print("Refresh token failed - doing interactive login.")
    return get_tokens_interactive()


# ------- Saxo API call -------
def get_open_positions(access_token):
    url = f"{GATEWAY_BASE}/port/v1/positions/me"
    params = {"FieldGroups": "PositionBase,DisplayAndFormat,Greeks,PositionView"}
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    if r.status_code == 401:
        raise RuntimeError("Unauthorized (401). Check scopes or re-login.")
    r.raise_for_status()
    return r.json()


# ------- PDF generation -------
def positions_to_pdf(data: dict, pdf_path: str):
    rows = data.get("Data") or data.get("Positions") or []
    # Fallback: if ReportLab is not available, write a simple HTML table instead
    if not HAVE_REPORTLAB:
        html_path = os.path.splitext(pdf_path)[0] + ".html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<html><head><meta charset=\"utf-8\"><title>Positions</title></head><body>\n")
            f.write("<h1>Saxo - Open Positions</h1>\n")
            if not rows:
                f.write("<p>No open positions found.</p>\n")
            else:
                f.write("<table border=\"1\" cellspacing=\"0\">\n")
                f.write("<tr><th>AccountId</th><th>Symbol</th><th>Uic</th><th>AssetType</th><th>Amount</th><th>OpenPrice</th><th>CurrentPrice</th><th>Exposure</th><th>PnL</th></tr>\n")
                for p in rows:
                    base = p.get("PositionBase", {})
                    fmt = p.get("DisplayAndFormat", {})
                    view = p.get("PositionView", {})
                    f.write("<tr>")
                    f.write(f"<td>{base.get('AccountId','')}</td>")
                    f.write(f"<td>{fmt.get('Symbol', base.get('Symbol',''))}</td>")
                    f.write(f"<td>{base.get('Uic','')}</td>")
                    f.write(f"<td>{base.get('AssetType','')}</td>")
                    f.write(f"<td>{base.get('Amount','')}</td>")
                    f.write(f"<td>{base.get('OpenPrice','')}</td>")
                    f.write(f"<td>{view.get('CurrentPrice','')}</td>")
                    f.write(f"<td>{view.get('Exposure','')}</td>")
                    f.write(f"<td>{view.get('ProfitLossOnTrade','')}</td>")
                    f.write("</tr>\n")
                f.write("</table>\n")
            f.write("</body></html>\n")
        return html_path
    table_data = [[
        "AccountId", "Symbol", "Uic", "AssetType", "Amount",
        "OpenPrice", "CurrentPrice", "Exposure", "PnL"
    ]]
    for p in rows:
        base = p.get("PositionBase", {})
        fmt = p.get("DisplayAndFormat", {})
        view = p.get("PositionView", {})
        table_data.append([
            str(base.get("AccountId", "")),
            str(fmt.get("Symbol", base.get("Symbol", ""))),
            str(base.get("Uic", "")),
            str(base.get("AssetType", "")),
            str(base.get("Amount", "")),
            str(base.get("OpenPrice", "")),
            str(view.get("CurrentPrice", "")),
            str(view.get("Exposure", "")),
            str(view.get("ProfitLossOnTrade", "")),
        ])
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4), title="Saxo Open Positions")
    styles = getSampleStyleSheet()
    elems = [Paragraph("Saxo - Open Positions", styles["Title"]), Spacer(1, 12)]
    if not rows:
        elems.append(Paragraph("No open positions found.", styles["Normal"]))
    else:
        tbl = Table(table_data, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("ALIGN", (0, 1), (-1, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.beige]),
        ]))
        elems.append(tbl)
    doc.build(elems)


# ------- Main -------
def main():
    print(f"Environment: {ENV}")
    print(f"Gateway: {GATEWAY_BASE}")
    print(f"Auth base: {AUTH_BASE}")
    print(f"Auth URL: {AUTH_URL}")
    print(f"Token URL: {TOKEN_URL}")
    print(f"Redirect URI: {REDIRECT_URI}")
    tokens = get_valid_tokens()
    access_token = tokens["access_token"]
    positions = get_open_positions(access_token)

    with open(OUT_RAW, "w", encoding="utf-8") as f:
        json.dump(positions, f, indent=2)
    print(f"Saved raw JSON to {OUT_RAW}")

    positions_to_pdf(positions, OUT_PDF)
    print(f"Saved PDF to {OUT_PDF}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        raise
