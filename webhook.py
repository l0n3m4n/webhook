#!/usr/bin/env python3

import http.server
import socketserver
import subprocess
import threading
import logging
import argparse
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


# Custom handler to print and log headers
class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        headers_str = f"\n[Request] {self.client_address[0]} - Path: {self.path}\n"
        for key, value in self.headers.items():
            headers_str += f"{key}: {value}\n"
        logging.info(headers_str)
        super().do_GET()

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
    if shutil.which("cloudflared") is None:
        print(f"{RED}[!] cloudflared is not installed. Please install it first.{RESET}")
        print(f"{CYAN}    https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/{RESET}")
        sys.exit(1)

    print(f"{BLUE}[i] Starting cloudflared tunnel on port {port}...{RESET}", flush=True)
    try:
        subprocess.run(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            check=True
        )
    except subprocess.CalledProcessError:
        print(f"{RED}[!] cloudflared tunnel failed. Exiting.{RESET}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Serve a local directory over HTTP and expose it via Serveo or cloudflared tunnel.",
        epilog=f"{BLUE}Example:{RESET} sudo python3 webhook.py -p 8080 -d /var/www/html"
    )
    parser.add_argument("-p", "--port", type=int, default=80, help="Local port to serve (default: 80)")
    parser.add_argument("-d", "--directory", default=".", help="Directory to serve (default: current dir)")
    args = parser.parse_args()

    server_thread = threading.Thread(target=start_http_server, args=(args.directory, args.port))
    server_thread.daemon = True
    server_thread.start()

    start_serveo_tunnel(args.port)


if __name__ == "__main__":
    print_banner()
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Interrupted by user. Exiting...{RESET}")
        sys.exit(0)
