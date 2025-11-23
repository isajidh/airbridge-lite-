import http.server
import socketserver
import os
import sys
import urllib.parse
import qrcode
from PIL import Image

PORT = 8000
SAVE_DIR = os.path.abspath(os.path.join(os.getcwd(), "../"))  # one level up
os.makedirs(SAVE_DIR, exist_ok=True)

HTML_PAGE = f"""
<html>
<head>
<title>Multi-file Upload</title>
</head>
<body>
<h2>Upload Multiple Files</h2>
<input type="file" id="files" multiple><br><br>
<button onclick="upload()">Upload</button>
<progress id="bar" max="100" value="0" style="width:300px;"></progress>
<div id="status"></div>

<script>
function upload() {{
    var files = document.getElementById('files').files;
    var formData = new FormData();
    for (var i = 0; i < files.length; i++) {{
        formData.append("files", files[i]);
    }}

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);

    xhr.upload.onprogress = function(e) {{
        if (e.lengthComputable) {{
            var percent = (e.loaded / e.total) * 100;
            document.getElementById('bar').value = percent;
            document.getElementById('status').innerText = Math.round(percent) + "% uploaded";
        }}
    }};

    xhr.onload = function() {{
        if (xhr.status == 200) {{
            document.getElementById('status').innerHTML = xhr.responseText;
            document.getElementById('bar').value = 0;
        }} else {{
            document.getElementById('status').innerText = "Upload failed!";
        }}
    }};
    xhr.send(formData);
}}
</script>
</body>
</html>
"""

class UploadHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers.get("Content-Type")
        boundary = content_type.split("boundary=")[1].encode()

        remaining = content_length
        body = b""
        chunk_size = 4096

        print(f"Receiving {content_length} bytes...")
        while remaining > 0:
            read_size = min(chunk_size, remaining)
            chunk = self.rfile.read(read_size)
            body += chunk
            remaining -= len(chunk)

            progress = (content_length - remaining) / content_length * 100
            sys.stdout.write(f"\rTerminal Progress: {progress:.1f}%")
            sys.stdout.flush()
        print("\nUpload complete. Processing files...")

        # Split and save files
        parts = body.split(boundary)
        saved_files = []

        for part in parts:
            if b'filename=' in part:
                headers, file_data = part.split(b"\r\n\r\n", 1)
                file_data = file_data.rstrip(b"\r\n--")
                header_str = headers.decode(errors='ignore')
                filename = header_str.split("filename=")[1].split('"')[1]

                if filename:
                    filename = os.path.basename(urllib.parse.unquote(filename))
                    save_path = os.path.join(SAVE_DIR, filename)
                    with open(save_path, "wb") as f:
                        f.write(file_data)
                    saved_files.append(filename)
                    print(f"Saved file: {filename} ({len(file_data)} bytes)")

        # Respond to browser
        self.send_response(200)
        self.end_headers()
        if saved_files:
            msg = "Uploaded files:<br>" + "<br>".join(saved_files)
            self.wfile.write(msg.encode())
        else:
            self.wfile.write(b"No files uploaded.")

with socketserver.TCPServer(("", PORT), UploadHandler) as httpd:
    print(f"Serving at port {PORT}, saving files to {SAVE_DIR}")
    httpd.serve_forever()
