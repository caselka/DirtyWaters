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
   ```bash
   # Add these lines to /etc/tor/torrc
   ControlPort 9051
   CookieAuthentication 1
   SocksPort 9050
   ```

3. Start Tor service:
   ```bash
   sudo systemctl start tor
   sudo systemctl enable tor
   ```

4. Verify Tor is running:
   ```bash
   sudo systemctl status tor
   ```

### Python Dependencies
The tool requires the following Python packages (automatically installed):
- `requests[socks]` - HTTP requests with SOCKS proxy support
- `stem` - Python controller library for Tor
- `PyYAML` - YAML configuration file parsing

## 🚀 Installation

1. Clone or download the project:
   ```bash
   git clone <repository-url>
   cd dirty-waters
   ```

2. Install dependencies:
   ```bash
   pip install requests[socks] stem pyyaml
   ```

3. Ensure Tor is running:
   ```bash
   sudo systemctl start tor
   ```

## ⚙️ Configuration

Edit `config.yaml` to configure your attack parameters:

```yaml
# Target Configuration
target_url: "http://example.com/wp-login.php"  # WordPress login URL
username: "admin"                              # Target username

# Password Configuration  
password_file: "passwords.txt"                 # Path to password list

# Tor Network Configuration
proxy: "socks5h://127.0.0.1:9050"             # Tor SOCKS5 proxy
control_port: 9051                             # Tor control port
control_password: ""                           # Tor control password

# Detection Configuration
success_indicators:                            # Indicators of successful login
  - "/wp-admin/"                              # Redirect to admin panel
  - "wp-admin-bar"                            # Admin bar in HTML

failure_indicators:                            # Indicators of failed login
  - "The password you entered for the username"

# Timing Configuration
attempts_per_circuit: 10                       # New Tor circuit every N attempts
rate_limit: 2                                 # Seconds between requests
timeout: 30                                   # HTTP request timeout
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `target_url` | WordPress login URL | Required |
| `username` | Target username | Required |
| `password_file` | Path to password list | Required |
| `proxy` | Tor SOCKS proxy URL | `socks5h://127.0.0.1:9050` |
| `control_port` | Tor control port | `9051` |
| `success_indicators` | Success detection patterns | `["/wp-admin/", "wp-admin-bar"]` |
| `failure_indicators` | Failure detection patterns | `["The password you entered for the username"]` |
| `attempts_per_circuit` | Circuit rotation frequency | `10` |
| `rate_limit` | Delay between requests (seconds) | `2` |
| `timeout` | HTTP timeout (seconds) | `30` |

## 🎯 Usage

### Basic Usage
```bash
python main.py
```

### Custom Configuration
```bash
python main.py --config custom_config.yaml
```

### Command Line Options
```bash
python main.py --help
```

### Example Session
```bash
$ python main.py
================================================================================
Dirty Waters - WordPress Brute Force Tool v1.0.0
Advanced Security Testing via Tor Network
================================================================================

[Ethical disclaimer appears]
Do you agree to use this tool ethically and legally? (yes/no): yes

Starting Dirty Waters...
Configuration file: config.yaml
2024-01-15 10:30:15 - INFO - Configuration loaded successfully
2024-01-15 10:30:15 - INFO - Loaded 500 passwords from passwords.txt
2024-01-15 10:30:16 - INFO - Successfully connected to Tor control port 9051
2024-01-15 10:30:17 - INFO - Tor connection established. Exit IP: 185.220.101.32
2024-01-15 10:30:17 - INFO - Starting WordPress brute-force attack
2024-01-15 10:30:17 - INFO - Target: http://example.com/wp-login.php
2024-01-15 10:30:17 - INFO - Username: admin
2024-01-15 10:30:17 - INFO - Passwords to test: 500
2024-01-15 10:30:18 - INFO - Attempt 1/500: Testing password '123456'
...
```

## 📊 Output and Logging

### Console Output
- Real-time progress updates
- Success/failure status for each attempt
- Circuit rotation notifications
- Final summary report

### Log Files
- Detailed logs saved to `logs/dirty_waters.log`
- Includes timestamps, IP addresses, and response details
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### Final Report
```
================================================================================
                              ATTACK SUMMARY                                  
================================================================================
| Target URL: http://example.com/wp-login.php                               |
| Username: admin                                                            |
| Total attempts: 50                                                         |
| Elapsed time: 125.50 seconds                                              |
| Average time per attempt: 2.51 seconds                                    |
| Success: Yes                                                               |
| Found password: password123                                               |
================================================================================
```

## 🔧 Advanced Features

### Circuit Rotation
- Automatic Tor circuit rotation every N attempts
- Manual circuit rotation on demand
- Circuit status monitoring

### Rate Limiting
- Configurable delays between requests
- Respectful testing to avoid service disruption
- Timeout handling for slow responses

### Detection Engine
- Multiple success/failure indicators
- HTTP redirect detection
- HTML content analysis
- Configurable detection patterns

### Error Handling
- Network timeout recovery
- Tor connection monitoring
- Clean exit on interruption
- Progress preservation

## 🛠️ Troubleshooting

### Common Issues

**Tor Connection Failed**
```bash
# Check if Tor is running
sudo systemctl status tor

# Check Tor configuration
sudo cat /etc/tor/torrc | grep -E "(ControlPort|SocksPort)"

# Restart Tor service
sudo systemctl restart tor
```

**Permission Denied on Control Port**
```bash
# Add user to debian-tor group (Ubuntu/Debian)
sudo usermod -a -G debian-tor $USER

# Or run with sudo (not recommended)
sudo python main.py
```

**Target Unreachable**
```bash
# Test direct connection
curl -x socks5h://127.0.0.1:9050 http://target-url.com

# Check target URL format
# Ensure URL includes full path to wp-login.php
```

**Password List Issues**
```bash
# Check file exists and is readable
ls -la passwords.txt

# Verify file encoding (should be UTF-8)
file passwords.txt
```

## 📁 Project Structure

```
dirty-waters/
├── dirty_waters/              # Main package
│   ├── __init__.py           # Package initialization
│   ├── brute_forcer.py       # Main brute-force engine
│   ├── tor_controller.py     # Tor network management
│   └── utils.py              # Utility functions
├── logs/                     # Log directory
│   └── .gitkeep             # Ensure directory exists
├── config.yaml              # Configuration file
├── main.py                  # Application entry point
├── passwords.txt            # Sample password list
├── README.md               # This file
└── .gitignore              # Git ignore rules
```

## 🔒 Security Considerations

### Responsible Use
- Only test systems you own or have permission to test
- Respect rate limits to avoid service disruption
- Use strong passwords for your own systems
- Follow responsible disclosure for vulnerabilities

### Anonymity
- All traffic routed through Tor network
- Automatic IP rotation via circuit changes
- No local storage of sensitive data
- Clean exit prevents data leakage

### Limitations
- Requires working Tor connection
- Subject to Tor network latency
- May be detected by WAFs or rate limiting
- Success depends on password list quality

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows Python style guidelines
- All features include comprehensive tests
- Documentation is updated accordingly
- Ethical use guidelines are maintained

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Legal Notice

This tool is provided for educational and authorized security testing purposes only. Users are solely responsible for ensuring their use complies with applicable laws and regulations. Unauthorized access to computer systems is illegal and may result in criminal charges and civil liability.

The authors disclaim any responsibility for misuse of this tool.

## 🔗 Resources

### Password Lists
- [SecLists](https://github.com/danielmiessler/SecLists) - Comprehensive security testing lists
- [RockYou](https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt) - Popular password list
- [Common Passwords](https://github.com/danielmiessler/SecLists/tree/master/Passwords) - Various password collections

### Tor Resources
- [Tor Project](https://www.torproject.org/) - Official Tor documentation
- [Stem Documentation](https://stem.torproject.org/) - Python Tor controller library
- [Tor Configuration](https://2019.www.torproject.org/docs/tor-manual.html.en) - Complete configuration guide

### WordPress Security
- [WordPress Security](https://wordpress.org/support/article/hardening-wordpress/) - Official security guide
- [OWASP WordPress](https://owasp.org/www-project-wordpress-security/) - Security testing methodology
   