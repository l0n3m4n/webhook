#!/usr/bin/env python3

import http.server
import socketserver
import subprocess
import threading
import logging
import socket 
import argparse
import textwrap
import requests
import cgi 
import time 
import os
import sys
import shutil
from http.server import SimpleHTTPRequestHandler
from datetime import datetime

# ANSI terminal colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

# Logging setup
logging.basicConfig(
    filename="headers.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def print_banner():
    banner = rf"""{CYAN}
     .->    (`-')  _<-.(`-')  (`-').->                      <-.(`-')  
 (`(`-')/`) ( OO).-/ __( OO)  (OO )__      .->        .->    __( OO)  
,-`( OO).',(,------.'-'---.\ ,--. ,'-'(`-')----. (`-')----. '-'. ,--. 
|  |\\  |  | |  .---'| .-. (/ |  | |  |( OO).-.  '( OO).-.  '|  .'   / 
|  | '.|  |(|  '--. | '-' `.)|  `-'  |( _) | |  |( _) | |  ||      /) 
|  |.'.|  | |  .--' | /`'.  ||  .-.  | \\|  |)|  | \\|  |)|  ||  .   '  
|   ,'.   | |  `---.| '--'  /|  | |  |  '  '-'  '  '  '-'  '|  |\\   \\ 
`--'   '--' `------'`------' `--' `--'   `-----'    `-----' `--' '--' 
     Author: l0n3m4n | Version: 1.0 | Serveo/Cloudflared Tunnel 
{RESET}"""
    print(banner)

# Check if a port is available
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            return True
        except OSError:
            return False

# auto-detect missing binaries 
def require_binary(binary_name, install_hint=None):
    """Check if a binary exists. If not, print install instructions and exit."""
    if shutil.which(binary_name) is None:
        print(f"{RED}[!] Required binary '{binary_name}' not found.{RESET}")
        if install_hint:
            print(f"{YELLOW}[i] Install it with:{RESET}\n  {install_hint}")
        sys.exit(1)

def check_dependencies(args):
    """Check and enforce required binaries based on selected tunnel."""
    if args.serveo:
        require_binary("ssh", "sudo apt install openssh-client")
    elif args.cloudflared:
        require_binary("cloudflared", "https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/")
    elif args.ngrok:
        require_binary("ngrok", "https://ngrok.com/download")
    elif args.localtunnel:
        require_binary("lt", "npm install -g localtunnel")



# Custom handler to print and log headers
class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        headers_str = f"\n[Request] {self.client_address[0]} - Path: {self.path}\n"
        for key, value in self.headers.items():
            headers_str += f"{key}: {value}\n"
        logging.info(headers_str)
        super().do_GET()
    

    def do_POST(self):
        if self.path != "/upload":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found.\n")
            return

        ctype, pdict = cgi.parse_header(self.headers.get('content-type', ''))
        if ctype == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                    environ={'REQUEST_METHOD':'POST'},
                                    keep_blank_values=True)

            if 'file' in form:
                file_item = form['file']
                filename = os.path.basename(file_item.filename)
                file_data = file_item.file.read()

                with open(filename, 'wb') as f:
                    f.write(file_data)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"File '{filename}' received and saved.\n".encode())

                # Logging
                logging.info(f"\n[POST] {self.client_address[0]} uploaded file: {filename}")
                return

        # If not multipart/form-data or 'file' missing
        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"Bad Request: Expected multipart/form-data with file field.\n")

    def log_message(self, format, *args):
        message = format % args
        if message.startswith("code"):
            return
        parts = message.split()
        if len(parts) >= 3:
            status_code = parts[-2]
            request_path = parts[1] if len(parts) > 1 else ""
            color = GREEN if status_code.startswith("2") else RED
            status_text = f"{color}[{status_code}]{RESET}"
            if status_code == "404":
                print(f"{status_text} - Not Found: {request_path}", flush=True)
            else:
                print(f"{status_text} - {self.requestline}", flush=True)

def start_http_server(directory, port):
    os.chdir(directory)
    handler = RequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"{GREEN}[+] Serving {directory} on port {port}{RESET}")
        httpd.serve_forever()


def start_serveo_tunnel(port):
    require_binary("ssh", "sudo apt install openssh-client")

    print(f"{BLUE}[i] Attempting to open Serveo tunnel on port {port}...{RESET}", flush=True)
    try:
        subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{port}", "serveo.net"],
            check=True
        )
    except subprocess.CalledProcessError:
        print(f"{YELLOW}[!] Serveo tunnel failed. Falling back to cloudflared...\n{RESET}")
        start_cloudflared_tunnel(port)


def start_cloudflared_tunnel(port):
    require_binary("cloudflared", "https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/")

    print(f"{BLUE}[i] Starting cloudflared tunnel on port {port}...{RESET}", flush=True)
    try:
        subprocess.run(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            check=True
        )
    except subprocess.CalledProcessError:
        print(f"{RED}[!] cloudflared tunnel failed. Exiting.{RESET}")
        sys.exit(1)


def start_ngrok_tunnel(port):
    require_binary("ngrok", "https://ngrok.com/download")

    print(f"{BLUE}[i] Starting ngrok tunnel on port {port}...{RESET}")

    try:
        # Start ngrok in the background
        ngrok_process = subprocess.Popen(["ngrok", "http", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for ngrok's web interface to become available
        time.sleep(3)  # give ngrok time to start

        # Try to get the tunnel URL from the ngrok API
        try:
            resp = requests.get("http://localhost:4040/api/tunnels")
            tunnels = resp.json()["tunnels"]
            public_urls = [t["public_url"] for t in tunnels if t["proto"] == "http" or t["proto"] == "https"]

            if public_urls:
                print(f"{GREEN}[+] Ngrok tunnel is live!{RESET}")
                for url in public_urls:
                    print(f"{CYAN}[*] Public URL: {WHITE}{url}{RESET}")
            else:
                print(f"{YELLOW}[!] No public URLs found from ngrok API.{RESET}")

        except requests.ConnectionError:
            print(f"{RED}[!] Unable to connect to ngrok API (http://localhost:4040).{RESET}")
            ngrok_process.terminate()
            sys.exit(1)

        # Keep the process running so ngrok stays alive
        ngrok_process.wait()

    except subprocess.CalledProcessError:
        print(f"{RED}[!] ngrok tunnel failed. Exiting.{RESET}")
        sys.exit(1)

def start_localtunnel(port):
    require_binary("lt", "npm install -g localtunnel")

    print(f"{BLUE}[i] Starting localtunnel tunnel on port {port}...{RESET}")
    try:
        subprocess.run(["lt", "--port", str(port)], check=True)
    except subprocess.CalledProcessError:
        print(f"{RED}[!] localtunnel failed. Exiting.{RESET}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
    description="📡 Serve a local directory and expose it via a tunnel (Serveo, Cloudflared, Ngrok, LocalTunnel).",
    epilog=textwrap.dedent(f"""{CYAN}
    Examples:
      python3 webhook.py -p 8080 --serveo
      python3 webhook.py -p 80 -d /var/www/html --cloudflared
      python3 webhook.py -p 3000 -d ~/my-site --ngrok
      python3 webhook.py -p 8080 -d ~/my-site --localtunnel
    {RESET}"""),
    formatter_class=argparse.RawDescriptionHelpFormatter
)
  
    parser.add_argument("-p", "--port", type=int, default=80, help="Local port to serve (default: 80)")
    parser.add_argument("-d", "--directory", default=".", help="Directory to serve (default: current dir)")
    
    tunnel_group = parser.add_mutually_exclusive_group(required=True)
    tunnel_group.add_argument("--serveo", action="store_true", help="Use Serveo tunnel")
    tunnel_group.add_argument("--cloudflared", action="store_true", help="Use Cloudflared tunnel")
    tunnel_group.add_argument("--ngrok", action="store_true", help="Use Ngrok tunnel")
    tunnel_group.add_argument("--localtunnel", action="store_true", help="Use LocalTunnel tunnel")

    
    args = parser.parse_args()
    check_dependencies(args)
     
     
    if not is_port_available(args.port):
        print(f"{RED}[!] Port {args.port} is already in use. Choose a different port.{RESET}")
        sys.exit(1)
    
    threading.Thread(target=start_http_server, args=(args.directory, args.port), daemon=True).start()

    # Start selected tunnel
    if args.serveo:
        start_serveo_tunnel(args.port)
    elif args.cloudflared:
        start_cloudflared_tunnel(args.port)
    elif args.ngrok:
        start_ngrok_tunnel(args.port)
    elif args.localtunnel:
        start_localtunnel(args.port)


if __name__ == "__main__":
    print_banner()
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Interrupted by user. Exiting...{RESET}")
        sys.exit(0)
