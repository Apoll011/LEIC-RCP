import io
import os
import socket

# ALgums Dicionarios com valors a serem usados
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


#Cria um classe servidor
class HTTPServer:
    def __init__(self, port: int = 80, path: str = "./web") -> None:
        self.base_path = path
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Cria a conexção socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # Define a conexção como TCP
        self.sock.bind(('0.0.0.0', port))                                   # A conexcao faz bind na porta pedida

        self.sock.listen()                                                  # COmeça a escutar por pedidos de conexção

    def loop(self) -> None:
        while True:
            conn, _ = self.sock.accept()                                    # Cliente conectou

            with conn:
                request_stream = conn.makefile('rb')                        # Crie arquivos virtuais para leitura e escrita dos dados
                response_stream = conn.makefile('wb')
                try: 
                    self.handle(request_stream, response_stream)            # Pedido do Cliente
                except Exception as e:
                    self.error(response_stream, e)
                conn.close()

    def parse_request(self, stream: io.BufferedIOBase):
        request = stream.readline().decode().rstrip('\r\n').split(' ')

        request_type = request[0]
        path = request[1]

        headers = {} 
        line = stream.readline().decode()
        while line not in ('\r\n', '\n', '\r', ''):
            header = line.rstrip('\r\n').split(': ')
            headers[header[0]] = header[1]
            line = stream.readline().decode()
        
        full_path = self.base_path + path

        if (os.path.isdir(full_path)):
            full_path += "/index.html"

        return request_type, full_path, headers

    def build_response(self, path):
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


    def handle(self, stream: io.BufferedIOBase, response_stream: io.BufferedIOBase):
        type, path, _ = self.parse_request(stream)
        
        if type != "GET":
            self.not_implemented(response_stream)
            return
        
        if not os.path.exists(path):
            self.not_found(response_stream, path)
            return
        
        response_headers, content = self.build_response(path)
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
    <p>O caminho {path.lstrip(self.base_path)} não foi encontrado.</p>
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
    
    def error(self, write_stream: io.BufferedIOBase, e: Exception): 
        self.send_to_client(write_stream, 500, {
            "Content-Type": "text/html; charset=UTF-8",
            "Content-Length": 139 + len(str(e)),
            "Connection": "close"
        }, bytes(f"""
<html>
  <head><title>500 Server Error</title></head>
  <body>
    <h1>Server Error</h1>
    <p>Occorreu um erro: {str(e)}</p>
  </body>
</html>
""", "utf-8"))
        
    def send_to_client(self, write_stream: io.BufferedIOBase, code: int, headers: dict[str, str|int], content: bytes):
        headers_str = "".join([f"{key}: {value}\r\n" for key, value in headers.items()])

        resp_content = f"HTTP/1.1 {code} {http_responses[code]}\r\n{headers_str}\r\n"

        write_stream.write(bytes(resp_content, "utf-8") + content)
        write_stream.flush()

    def close(self, *args) -> None:
        self.sock.close()

if __name__ == "__main__":
    server = HTTPServer(8100)
    try:
        server.loop()
    except KeyboardInterrupt:
        server.close()