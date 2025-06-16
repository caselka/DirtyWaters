"""
Dirty Waters - Advanced WordPress Brute Force Tool for Ethical Security Testing

A highly modular brute-force tool designed for authorized penetration testing
of WordPress login forms via the Tor network.

Author: Security Research Team
Version: 1.0.0
License: MIT

IMPORTANT: This tool is for educational and authorized security testing only.
Unauthorized use is illegal and unethical.
"""

__version__ = "1.0.0"
__author__ = "Security Research Team"
__license__ = "MIT"

from .tor_controller import TorController
from .brute_forcer import WordPressBruteForcer
from .utils import setup_logging, format_output, RetryHandler

__all__ = [
    'TorController',
    'WordPressBruteForcer', 
    'setup_logging',
    'format_output',
    'RetryHandler'
]
