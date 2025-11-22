import socket
import subprocess
import sys
import os

def get_local_ip():
    """Detect the active LAN/Wi-Fi IPv4 address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public IP, doesn't actually send data
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def main():
    ip = get_local_ip()
    print(f"\n🔥 AirBridge Lite starting...")
    print(f"🌐 Your Wi-Fi IP: http://{ip}:8000\n")

    server_file = "full_upload_server.py"
    if not os.path.exists(server_file):
        print(f"❌ Missing {server_file}")
        sys.exit(1)

    try:
        subprocess.run([sys.executable, server_file])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

if __name__ == "__main__":
    main()
