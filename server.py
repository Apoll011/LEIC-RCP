import io
import os
import socket

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
                    request_stream=request_stream,
                    response_stream=response_stream
                )

    def handle(self, request_stream: io.BufferedIOBase, response_stream: io.BufferedIOBase):
        ...

    def exists(self,path):
        return os.path.exists(path)

    #./web/index.html, ./web/icon.png
    def response(self, path):
        extensao = path.split(".")[-1]

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

        content_type = content_types[extensao]
        """
        HTTP/1.1 200 OK
        Content-Type: text/html; charset=UTF-8
        Content-Length: 128
        Connection: close

       
        """

        headers = {
            "Content-Type": content_type,
            "Content-Length": os.path.getsize(path),
            "Connection": "close"
        }

        return headers, open(path, "rb").read()

    def __enter__(self) -> 'HTTPServer':
        return self

    def __exit__(self, *args) -> None:
        self.sock.close()

if __name__ == "__main__":
    with HTTPServer(8100) as server:
        server.loop()