"""
Utility Functions

Provides logging setup, output formatting, retry handling, and other utility
functions used throughout the Dirty Waters application.
"""

import os
import logging
import time
from typing import List, Callable, Any, Optional
from functools import wraps


def setup_logging(log_level: str = "INFO", log_file: str = "logs/dirty_waters.log") -> logging.Logger:
    """
    Setup logging configuration with both file and console output.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logger = logging.getLogger('dirty_waters')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger


def format_output(title: str, lines: List[str], width: int = 80) -> str:
    """
    Format output with a decorative border for better readability.
    
    Args:
        title (str): Title for the output block
        lines (List[str]): Lines of content
        width (int): Width of the output block
        
    Returns:
        str: Formatted output string
    """
    border = "=" * width
    title_line = f"| {title.center(width - 4)} |"
    separator = "=" * width
    
    output_lines = [border, title_line, separator]
    
    for line in lines:
        # Handle long lines by wrapping
        if len(line) <= width - 4:
            output_lines.append(f"| {line.ljust(width - 4)} |")
        else:
            # Simple word wrapping
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line + " " + word) <= width - 4:
                    current_line = current_line + " " + word if current_line else word
                else:
                    if current_line:
                        output_lines.append(f"| {current_line.ljust(width - 4)} |")
                    current_line = word
            if current_line:
                output_lines.append(f"| {current_line.ljust(width - 4)} |")
    
    output_lines.append(border)
    return "\n".join(output_lines)


def format_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Create a simple text-based progress bar.
    
    Args:
        current (int): Current progress value
        total (int): Total/maximum value
        width (int): Width of the progress bar
        
    Returns:
        str: Formatted progress bar string
    """
    if total == 0:
        percentage = 0
    else:
        percentage = min(100, (current / total) * 100)
    
    filled_width = int((percentage / 100) * width)
    bar = "█" * filled_width + "░" * (width - filled_width)
    
    return f"[{bar}] {percentage:.1f}% ({current}/{total})"


class RetryHandler:
    """
    Handle retry logic for network operations and other fallible actions.
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
        """
        Initialize retry handler with configuration.
        
        Args:
            max_retries (int): Maximum number of retry attempts
            base_delay (float): Base delay between retries in seconds
            backoff_factor (float): Multiplier for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.logger = logging.getLogger(__name__)
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func (Callable): Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result of successful function execution
            
        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.base_delay * (self.backoff_factor ** attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_exception
    
    def retry_decorator(self, exceptions: tuple = (Exception,)):
        """
        Decorator for adding retry logic to functions.
        
        Args:
            exceptions (tuple): Tuple of exception types to catch and retry
            
        Returns:
            Callable: Decorated function with retry logic
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(self.max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < self.max_retries:
                            delay = self.base_delay * (self.backoff_factor ** attempt)
                            self.logger.warning(
                                f"Function {func.__name__} attempt {attempt + 1}/{self.max_retries + 1} failed: {e}. "
                                f"Retrying in {delay:.1f} seconds..."
                            )
                            time.sleep(delay)
                        else:
                            self.logger.error(f"Function {func.__name__} failed after {self.max_retries + 1} attempts")
                
                raise last_exception
            
            return wrapper
        return decorator


def validate_url(url: str) -> bool:
    """
    Validate if a URL has proper format.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    from urllib.parse import urlparse
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    import re
    
    # Remove invalid characters for filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def format_bytes(bytes_count: int) -> str:
    """
    Format byte count into human-readable string.
    
    Args:
        bytes_count (int): Number of bytes
        
    Returns:
        str: Formatted byte string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def check_tor_connection(proxy_url: str = "socks5h://127.0.0.1:9050", timeout: int = 10) -> bool:
    """
    Check if Tor proxy is accessible.
    
    Args:
        proxy_url (str): Tor SOCKS proxy URL
        timeout (int): Connection timeout in seconds
        
    Returns:
        bool: True if Tor is accessible, False otherwise
    """
    import requests
    
    try:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=timeout
        )
        
        return response.status_code == 200
    except Exception:
        return False
