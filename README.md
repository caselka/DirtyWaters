# Dirty Waters - WordPress Brute Force Tool

A highly modular, advanced brute-force tool designed for ethical testing of WordPress login forms via the Tor network.

## ⚠️ ETHICAL USE DISCLAIMER

**IMPORTANT: This tool is designed for educational purposes and authorized security testing only.**

- Only use this tool on systems you own or have explicit written permission to test
- Unauthorized access to computer systems is illegal and unethical
- The authors are not responsible for any misuse of this tool
- Always comply with local laws and regulations
- Respect rate limits and avoid causing service disruption

## 🔧 Features

- **Tor Network Integration**: Routes all traffic through Tor SOCKS5 proxy for anonymity
- **Circuit Management**: Automatic Tor circuit rotation using Stem library
- **Configurable Detection**: Customizable success/failure indicators
- **Rate Limiting**: Responsible testing with configurable delays
- **Progress Tracking**: Real-time progress monitoring and resumable sessions
- **Comprehensive Logging**: Detailed logs to both console and file
- **Clean Exit**: Keyboard interrupt handling with progress preservation
- **Modular Design**: Easily extensible and maintainable codebase

## 📋 Requirements

### System Requirements
- Python 3.12 or higher
- Tor daemon running and accessible
- Linux/macOS/Windows (tested on Linux)

### Tor Setup
1. Install Tor:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install tor
   
   # CentOS/RHEL/Fedora
   sudo dnf install tor
   
   # macOS
   brew install tor
   ```

2. Configure Tor (`/etc/tor/torrc`):
   