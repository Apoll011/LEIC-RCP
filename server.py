import io
import os
import socket

http_responses = {
    200: "OK",
    404: "Not Found",
    500: "Internal Server Error",
    501: "Not Implemented"
}

content_types = {
    "html": "text/html",
    "css": "text/css",
    "js": "text/javascript",
    "json": "application/json",
    "png": "image/png",    
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
    "zip": "application/zip",
    "mp3": "audio/mpeg",
    "mp4": "video/mp4",
    "txt": "text/plain"
}


class HTTPServer:
    def __init__(
        self, 
        port: int = 80, 
        path: str = "./web"
    ) -> None:
        self.path = path
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', port))

        self.sock.listen()

    def loop(self) -> None:
        while True:
            conn, addr = self.sock.accept()

            with conn:
                request_stream = conn.makefile('rb')
                response_stream = conn.makefile('wb')
                self.handle(
                    stream=request_stream,
                    response_stream=response_stream
                )

    def parse_request(self, stream: io.BufferedIOBase):
        request = stream.readline().decode().rstrip('\r\n')

        request_type = request.split(' ')[0]
        path = request.split(' ')[1]

        headers = {} 
        line = stream.readline().decode()
        while line not in ('\r\n', '\n', '\r', ''):
            header = line.rstrip('\r\n').split(': ')
            headers[header[0]] = header[1]
            line = stream.readline().decode()
        
        if path == "/":
            path = "/index.html"

        return request_type, path, headers

    def handle(self, stream: io.BufferedIOBase, response_stream: io.BufferedIOBase):
        type, path, headers = self.parse_request(stream)
        
        if type != "GET":
            self.not_implemented(response_stream)
            return

        full_path = self.path + path

        if not self.exists(full_path):
            self.not_found(response_stream, path)
            return
        
        response_headers, content = self.response(full_path)
        self.send_to_client(response_stream, 200, response_headers, content)

    def not_found(self, write_stream: io.BufferedIOBase, path: str):
                self.send_to_client(write_stream, 404, {
            "Content-Type": "text/html; charset=UTF-8",
            "Content-Length": 142 + len(path),
            "Connection": "close"
        }, bytes(f"""<html>
  <head><title>404 Not Found</title></head>
  <body>
    <h1>Not Found</h1>
    <p>O caminho {path} não foi encontrado.</p>
  </body>
</html>""", "utf-8"))
    
    def not_implemented(self, write_stream: io.BufferedIOBase): 
        self.send_to_client(write_stream, 501, {
            "Content-Type": "text/html; charset=UTF-8",
            "Content-Length": 174,
            "Connection": "close"
        }, bytes("""
<html>
  <head><title>501 Not Implemented</title></head>
  <body>
    <h1>Not Implemented</h1>
    <p>O método solicitado não é suportado pelo servidor.</p>
  </body>
</html>
""", "utf-8"))
        
    def send_to_client(self, write_stream: io.BufferedIOBase, code: int, headers: dict[str, str|int], content: bytes):
        headers_str = "".join([f"{key}: {value}\r\n" for key, value in headers.items()])

        resp_content = f"HTTP/1.1 {code} {http_responses[code]}\r\n{headers_str}\r\n"

        write_stream.write(bytes(resp_content, "utf-8") + content)
        write_stream.flush()

    def exists(self,path):
        return os.path.exists(path)

    #./web/index.html, ./web/icon.png
    def response(self, path):
        extensao = path.split(".")[-1]

        content_type = content_types[extensao]

        headers = {
            "Content-Type": content_type,
            "Content-Length": os.path.getsize(path),
            "Connection": "close"
        }

        with open(path, "rb") as file:
            content = file.read()

        return headers, content

    def __enter__(self) -> 'HTTPServer':
        return self

    def __exit__(self, *args) -> None:
        self.sock.close()

if __name__ == "__main__":
    with HTTPServer(8100) as server:
        server.loop()