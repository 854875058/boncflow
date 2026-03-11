import http.client
import http.server
import os
import socketserver
import urllib.parse
from typing import Iterable


ROOT = os.path.join(os.path.dirname(__file__), "..", "web", "dist")
PORT = 4180

PROXY_RULES = (
    ("/api/v1/admin", "10.132.19.82", 9381),
    ("/api", "10.132.19.82", 9380),
    ("/v1", "10.132.19.82", 9380),
)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
}


class ProxyPreviewHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self._maybe_proxy():
            return
        return self._serve_spa()

    def do_POST(self):
        if self._maybe_proxy():
            return
        self.send_error(501, "POST not supported for static route")

    def do_PUT(self):
        if self._maybe_proxy():
            return
        self.send_error(501, "PUT not supported for static route")

    def do_DELETE(self):
        if self._maybe_proxy():
            return
        self.send_error(501, "DELETE not supported for static route")

    def do_PATCH(self):
        if self._maybe_proxy():
            return
        self.send_error(501, "PATCH not supported for static route")

    def do_OPTIONS(self):
        if self._maybe_proxy():
            return
        self.send_response(204)
        self.end_headers()

    def _serve_spa(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            index = os.path.join(path, "index.html")
            if os.path.exists(index):
                return super().do_GET()
        if os.path.exists(path):
            return super().do_GET()
        self.path = "/index.html"
        return super().do_GET()

    def _maybe_proxy(self) -> bool:
        parsed = urllib.parse.urlsplit(self.path)
        for prefix, host, port in PROXY_RULES:
            if parsed.path.startswith(prefix):
                self._proxy_request(host, port)
                return True
        return False

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or "0")
        return self.rfile.read(length) if length > 0 else b""

    def _filtered_request_headers(self) -> dict:
        headers = {}
        for key, value in self.headers.items():
            if key.lower() in HOP_BY_HOP_HEADERS:
                continue
            headers[key] = value
        return headers

    def _proxy_request(self, host: str, port: int):
        body = self._read_body()
        conn = http.client.HTTPConnection(host, port, timeout=60)
        try:
            conn.request(
                self.command,
                self.path,
                body=body,
                headers=self._filtered_request_headers(),
            )
            resp = conn.getresponse()
            data = resp.read()

            self.send_response(resp.status, resp.reason)
            for key, value in resp.getheaders():
                if key.lower() in HOP_BY_HOP_HEADERS:
                    continue
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(data)
        finally:
            conn.close()


def run():
    class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadingTCPServer(("127.0.0.1", PORT), ProxyPreviewHandler) as httpd:
        print(f"preview-proxy-serving:http://127.0.0.1:{PORT}", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    run()
