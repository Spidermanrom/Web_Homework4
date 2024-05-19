import mimetypes
from pathlib import Path
import urllib.parse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socket
import datetime


BASE_DIR = Path()

HTTP_PORT = 3000
HTTP_HOST = '0.0.0.0'
UDP_PORT = 5000
UDP_IP = '127.0.0.1'
buffer_size = 1024

class GoitFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        print(route.query)
        match route.path:
            case "/":
                self.send_html("index.html")
            case "/blog":
                self.send_html("blog.html")
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
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()


def run_socket_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        addr = ip, port
        server.bind(addr)
        try:
            while True:
                data, address = server.recvfrom(buffer_size)
                data_parse = urllib.parse.unquote_plus(data.decode())
                data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
                result = {str(datetime.now()): data_dict}
                print(f'{result=}')
                with open("./storage/data.json", "a") as file:
                    json.dump(result, file, indent=4)
                server.sendto(data, address)
                print(f'Send data: {data.decode()} to: {address}')
        except KeyboardInterrupt:
            print('Bye server')
            
            
def run_socket_client(ip: str, port: int, data=None):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        server = ip, port
        client.sendto(data, server)
        print(f'Send data: {data.decode()} to server: {server}')
        response, address = client.recvfrom(buffer_size)
        print(f'Response data: {response.decode()} from address: {address}')


main_server = threading.Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
socket_server = threading.Thread(target=run_socket_server, args=(UDP_IP, UDP_PORT))
    
if __name__ == "__main__":
    main_server.start()
    socket_server.start()

