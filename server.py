import io
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

    def __enter__(self) -> 'HTTPServer':
        return self

    def __exit__(self, *args) -> None:
        self.sock.close()

if __name__ == "__main__":
    with HTTPServer(8100) as server:
        server.loop()