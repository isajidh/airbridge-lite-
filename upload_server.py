import http.server
import socketserver
import os

PORT = 8000

class UploadHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(b"""
        <html>
        <body>
            <h2>Upload File</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file"><br><br>
                <input type="submit" value="Upload">
            </form>
        </body>
        </html>
        """)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers.get("Content-Type")

        boundary = content_type.split("boundary=")[1].encode()
        body = self.rfile.read(content_length)

        # Split the body by the boundary
        parts = body.split(boundary)
        for part in parts:
            if b"filename=" in part:
                headers, file_data = part.split(b"\r\n\r\n", 1)
                file_data = file_data.rstrip(b"\r\n--")

                # Extract filename
                header_str = headers.decode()
                filename = header_str.split("filename=")[1].split('"')[1]

                with open(filename, "wb") as f:
                    f.write(file_data)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"File uploaded successfully.")
                return


with socketserver.TCPServer(("", PORT), UploadHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
