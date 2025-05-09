import http.server as hs
import os

if __name__ == "__main__":
    addr = (os.environ["HOST"], int(os.environ["PORT"]))
    httpd = hs.HTTPServer(addr, hs.SimpleHTTPRequestHandler)
    httpd.serve_forever()
