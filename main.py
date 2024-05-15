import mimetypes
from pathlib import Path
import urllib.parse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import logging


BASE_DIR = Path()

HTTP_PORT = 8080
HTTP_HOST = '0.0.0.0'

class GoitFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        print(route.query)
        match route.path:
            case "/":
                self.send_html("index.html")
            case "/blog":
                self.render_template("blog.html")
            case "/log_in":
                self.send_html("log_in.html")
            case _:
                file =  BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("error.html", 404)
                    
    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        print(data)
        self.send_response(302)
        self.send_header('Location', '/log_in')
        self.end_headers()

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header("Content-Type", mime_type)
        else:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, GoitFramework)
    logging.info("Starting http server")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()


main_server = threading.Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))

if __name__ == "__main__":
    main_server.start()
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

