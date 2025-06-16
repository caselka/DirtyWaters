# Dirty Waters - WordPress Brute Force Tool

A **modular, advanced brute-force tool** for ethical testing of WordPress login forms via the Tor network.

---

## ⚠️ ETHICAL USE DISCLAIMER

**This tool is for educational and authorized security testing purposes only.**

* ✅ Use only on systems you own or have explicit permission to test
* 🚫 Unauthorized access is illegal and unethical
* ⚡ The authors are **not responsible** for misuse
* 📜 Comply with **all local laws and regulations**
* 🕊 Respect rate limits to avoid service disruption

---

## 🔧 Features

* **Tor Network Integration:** Traffic routed through Tor SOCKS5 for anonymity
* **Automatic Circuit Rotation:** Uses Stem to rotate Tor circuits on demand
* **Customizable Detection:** Flexible success/failure indicators
* **Rate Limiting:** Configurable delays for responsible testing
* **Progress Tracking:** Resumable sessions with real-time console updates
* **Comprehensive Logging:** Console + file logs with configurable levels
* **Clean Exit:** Handles interrupts gracefully; preserves progress
* **Extensible Design:** Modular codebase ready for future enhancements

---

## 📋 Requirements

### System

* Python 3.12+
* Tor daemon running and accessible
* Linux/macOS/Windows (tested primarily on Linux)

### Tor Setup

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install tor

# Fedora/CentOS
sudo dnf install tor

# macOS (Homebrew)
brew install tor
```

Add to `/etc/tor/torrc`:

```
ControlPort 9051
CookieAuthentication 1
SocksPort 9050
```

Start and enable Tor:

```bash
sudo systemctl start tor
sudo systemctl enable tor
```

### Python dependencies

```bash
pip install requests[socks] stem pyyaml
```

---

## 🚀 Installation

```bash
git clone https://github.com/caselka/DirtyWaters
cd DirtyWaters
pip install -r requirements.txt  # If included
```

---

## ⚙️ Configuration

Example `config.yaml`:

```yaml
target_url: "http://example.com/wp-login.php"
username: "admin"
password_file: "passwords.txt"

proxy: "socks5h://127.0.0.1:9050"
control_port: 9051
control_password: ""

success_indicators:
  - "/wp-admin/"
  - "wp-admin-bar"
failure_indicators:
  - "The password you entered for the username"

attempts_per_circuit: 10
rate_limit: 2
timeout: 30
```

---

## 🎯 Usage

```bash
python main.py
```

or with a custom config:

```bash
python main.py --config myconfig.yaml
```

or see options:

```bash
python main.py --help
```

---

## 📊 Output

* **Console:** Real-time progress, Tor IP info, results
* **Logs:** Detailed logs saved to `logs/dirty_waters.log`
* **Report:** Final attack summary on completion

---

## 🛠️ Troubleshooting

✅ **Tor not connecting?**

```bash
sudo systemctl status tor
sudo systemctl restart tor
```

✅ **Permission issues?**

```bash
sudo usermod -a -G debian-tor $USER
newgrp debian-tor
```

✅ **Target unreachable?**

```bash
curl --socks5-hostname 127.0.0.1:9050 http://your-target.onion
```

---

## 📁 Project structure

```
DirtyWaters/
├── dirty_waters/
│   ├── brute_forcer.py
│   ├── tor_controller.py
│   └── utils.py
├── config.yaml
├── main.py
├── logs/
├── passwords.txt
└── README.md
```

---

## 🤝 Contributing

* Follow PEP8 / Python best practices
* Include tests for new features
* Document changes clearly
* Maintain ethical standards

---

## 📄 License

MIT License — see `LICENSE` file.

---

