import http.server
import asyncio

# Facebook Redirect handler class
class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, handle_authorization_response, *args, **kwargs):
        self.handle_authorization_response = handle_authorization_response
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Authorization successful</h1></body></html>")
        asyncio.create_task(self.handle_authorization_response(self.path))


def start(handle_code_callback, host: str="localhost", port: int=3000):
    server_address = (host, port)
    httpd = http.server.HTTPServer(
        server_address,
        lambda *args, **kwargs: RedirectHandler(handle_code_callback, *args, **kwargs),
    )
    httpd.handle_request()
