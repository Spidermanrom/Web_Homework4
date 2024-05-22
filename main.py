from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import pathlib
import socket
import urllib.parse
import mimetypes
import json


UDP_IP = '127.0.0.1'
UDP_PORT = 5000
HTTP_PORT = 3000
bufferSize = 1024


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/log_in':
            self.send_html_file('log_in.html')
        elif pr_url.path == '/blog':
            self.send_html_file('blog.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
            
    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())
            
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        
        
        run_socket_client(UDP_IP,UDP_PORT, data=data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('0.0.0.0', HTTP_PORT)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        
        
def run_socket_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        addr = ip, port
        server.bind(addr)
        try:
            while True:
                data, address = server.recvfrom(bufferSize)
                data_parse = urllib.parse.unquote_plus(data.decode())
                data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
                result = {str(datetime.now()): data_dict}
                print(f'{result=}')
                with open("./storage/data.json", "a") as file:
                    json.dump(result, file, indent=4)
                server.sendto(data, address)
                print(f'Send data: {data.decode()} to: {address}')
        except KeyboardInterrupt:
            print(f'Destroy server')
            
            
def run_socket_client(ip: str, port: int, data=None):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        server = ip, port
        client.sendto(data, server)
        print(f'Send data: {data.decode()} to server: {server}')
        response, address = client.recvfrom(bufferSize)
        print(f'Response data: {response.decode()} from address: {address}')


main_server = Thread(target=run)
socket_server = Thread(target=run_socket_server, args=(UDP_IP, UDP_PORT))


if __name__ == '__main__':
    main_server.start()
    socket_server.start()
    main_server.join()
    socket_server.join()