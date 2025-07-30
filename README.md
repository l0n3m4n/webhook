<h2 align="center">
  🪝 Webhook Server Tunnel
</h2>


 
<p align="center">
    <a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2Fl0n3m4n%2FSearchToolkit">
        <img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fl0n3m4n%2Fwebhook&label=Visitors&countColor=%2337d67a" />
    </a>
    <a href="https://www.facebook.com/UEVOLVJU">
        <img src="https://img.shields.io/badge/Facebook-%231877F2.svg?style=for-the-badge&logo=Facebook&logoColor=white" alt="Facebook">
    </a>
      <a href="https://www.twitter.com/UEVOLVJU">
        <img src="https://img.shields.io/badge/Twitter-%23000000.svg?style=for-the-badge&logo=X&logoColor=white" alt="X">
    </a>
    <a href="https://medium.com/@l0n3m4n">
        <img src="https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white" alt="Medium">
    </a>
    <a href="https://www.buymeacoffee.com/l0n3m4n">
        <img src="https://img.shields.io/badge/Buy%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee">
    </a>  
    <a href="mailto:ehph@proton.me">
      <img src="https://img.shields.io/badge/ProtonMail-6001D2?style=for-the-badge&logo=protonmail&logoColor=white" alt="ProtonMail">
    </a>
    <a href="https://github.com/l0n3m4n/SearchToolkit/blob/main/assets/contributing.md">
      <img src="https://img.shields.io/badge/Contribute-%23121011.svg?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</p>
<br/>

This Python script serves a local directory over HTTP and exposes it securely to the internet via a reverse tunnel using either:

- Serveo (SSH-based tunneling)
- Cloudflared (Cloudflare Tunnel)

It’s especially useful for:

- 📁 Hosting payloads or exploits during red team exercises or CTFs
- 📤 Exfiltrating data from compromised targets in a controlled environment
- 🧪 Testing XSS, CSRF, and SSRF vulnerabilities by exposing local endpoints
- 🌐 Simulating external servers during bug bounty engagements
- 💻 Demonstrating proof-of-concepts (PoCs) for file uploads or callbacks
- 🔐 Secure remote access to localhost web apps for testing
- 📡 Bypassing NAT/firewall restrictions without port forwarding

![Banner](assets/banner.png)

---

## 🚀 Features

- HTTP server using Python's built-in modules
- Logs all request headers to `headers.log`
- Expose server via:
  - 🌐 [Serveo](https://serveo.net)
  - ☁️ [Cloudflared](https://developers.cloudflare.com/cloudflare-one/)
- ANSI-colored terminal output
- Easy to use CLI

---

## 🛠 Requirements

- Python 3.6+
- `cloudflared` (only if Serveo is unavailable)

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/l0n3m4n/webhook.git
cd webhook

# Make it executable
chmod +x webhook.py

# (Optional) Install cloudflared if not using Serveo
sudo apt install cloudflared  # Or follow: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
```
## 📡 Usage
```bash
sudo python3 webhook.py -p 8080 -d /var/www/html
```
![usage](assets/usage.png)
![output](assets/output.png)
![status_codes](assets/status_codes.png)
![headers_log](assets/headers_logs.png)
- This will:
    - Serve files at http://localhost:8080
    - Attempt to expose it via Serveo
    - If Serveo is down, it will fallback to cloudflared tunnel

## 🔐 Security Notes
- This tool uses SSH for Serveo and a reverse proxy for Cloudflared.
- Ensure you trust any services you expose publicly.
