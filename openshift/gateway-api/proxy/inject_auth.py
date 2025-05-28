import os

from mitmproxy import http

TUF = os.environ.get("TUF_URL")
REKOR = os.environ.get("REKOR_URL")
FULCIO = os.environ.get("FULCIO_URL")
SEARCH = os.environ.get("SEARCH_URL")


TARGET_HOSTS = [
    TUF, REKOR, FULCIO, SEARCH
]

EXCLUDED_URLS = {
    FULCIO + "/api/v1/signingCert"
}

TOKEN = os.environ.get("TOKEN")

AUTH_HEADER = f"Bearer {TOKEN}"

print(f"Target hosts: {TARGET_HOSTS}")
print(f"Excluded urls: {EXCLUDED_URLS}")

def request(flow: http.HTTPFlow) -> None:
    host = f"{flow.request.scheme}://{flow.request.pretty_host}"
    path = flow.request.path.lstrip("/")
    full_url = f"{host}/{path}"

    if full_url in EXCLUDED_URLS:
        return  # Skip this exact host/path combination

    if host in TARGET_HOSTS:
        flow.request.headers["Authorization"] = AUTH_HEADER
        print(f"Injected Authorization header for {host}")
