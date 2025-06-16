#!/usr/bin/env python3
"""
Dirty Waters - WordPress Brute Force Tool
Main entry point for the application.

A highly modular brute-force tool designed for ethical testing of WordPress
login forms via the Tor network.

Usage:
    python main.py [--config CONFIG_FILE]

Author: Security Research Team
License: MIT

IMPORTANT: This tool is for educational and authorized security testing only.
Unauthorized use is illegal and unethical.
"""

import sys
import argparse
import os
from typing import Optional

from dirty_waters import WordPressBruteForcer
from dirty_waters.utils import setup_logging


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Dirty Waters - WordPress Brute Force Tool for Ethical Security Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                          # Use default config.yaml
    python main.py --config custom.yaml    # Use custom configuration
    
IMPORTANT: This tool is for authorized security testing only.
Unauthorized use is illegal and unethical.
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Dirty Waters v1.0.0'
    )
    
    return parser.parse_args()


def validate_environment() -> bool:
    """
    Validate that the environment is properly configured.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    # Check if running as root (not recommended)
    if os.geteuid() == 0:
        print("WARNING: Running as root is not recommended for security reasons.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    
    return True


def show_disclaimer() -> bool:
    """
    Show ethical use disclaimer and get user acknowledgment.
    
    Returns:
        bool: True if user accepts, False otherwise
    """
    disclaimer = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              ETHICAL USE DISCLAIMER                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  This tool is designed for educational purposes and authorized security      ║
║  testing only. By using this tool, you acknowledge that:                    ║
║                                                                              ║
║  • You will only use this tool on systems you own or have explicit          ║
║    written permission to test                                               ║
║  • Unauthorized access to computer systems is illegal and unethical         ║
║  • You are solely responsible for ensuring your use complies with           ║
║    applicable laws and regulations                                           ║
║  • The authors are not responsible for any misuse of this tool              ║
║  • You will respect rate limits and avoid causing service disruption        ║
║                                                                              ║
║  Unauthorized use may result in criminal charges and civil liability.       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    
    print(disclaimer)
    
    while True:
        response = input("Do you agree to use this tool ethically and legally? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            return True
        elif response.lower() in ['no', 'n']:
            return False
        else:
            print("Please answer 'yes' or 'no'.")


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Show banner
    print("=" * 80)
    print("Dirty Waters - WordPress Brute Force Tool v1.0.0")
    print("Advanced Security Testing via Tor Network")
    print("=" * 80)
    print()
    
    # Validate environment
    if not validate_environment():
        return 1
    
    # Show disclaimer and get acknowledgment
    if not show_disclaimer():
        print("Exiting. Tool usage requires ethical acknowledgment.")
        return 1
    
    print("\nStarting Dirty Waters...")
    print(f"Configuration file: {args.config}")
    
    # Check if configuration file exists
    if not os.path.exists(args.config):
        print(f"ERROR: Configuration file '{args.config}' not found.")
        print("Please create a configuration file or specify an existing one with --config")
        return 1
    
    try:
        # Initialize brute forcer
        brute_forcer = WordPressBruteForcer(config_file=args.config)
        
        # Run the attack
        success = brute_forcer.run()
        
        if success:
            print("\nAttack completed successfully.")
            return 0
        else:
            print("\nAttack completed with errors or was interrupted.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nAttack interrupted by user.")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
