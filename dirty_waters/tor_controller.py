"""
Tor Controller Module

Handles Tor network connections, circuit management, and control port operations.
Uses the Stem library to manage Tor circuits and send NEWNYM signals for IP rotation.
"""

import time
import logging
from typing import Optional, Dict, Any
from stem import Signal
from stem.control import Controller
from stem.connection import MissingPassword, IncorrectPassword


class TorController:
    """
    Manages Tor network connections and circuit rotation for anonymity.
    
    Handles control port connections, circuit renewal, and connection status monitoring.
    """
    
    def __init__(self, control_port: int = 9051, control_password: str = ""):
        """
        Initialize Tor controller with connection parameters.
        
        Args:
            control_port (int): Tor control port (default: 9051)
            control_password (str): Tor control password (default: empty)
        """
        self.control_port = control_port
        self.control_password = control_password
        self.controller = None
        self.logger = logging.getLogger(__name__)
        self.circuit_count = 0
        self.last_circuit_time = 0
        
    def connect(self) -> bool:
        """
        Establish connection to Tor control port.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.controller = Controller.from_port(port=self.control_port)
            
            # Authenticate with Tor
            if self.control_password:
                self.controller.authenticate(password=self.control_password)
            else:
                self.controller.authenticate()
                
            self.logger.info(f"Successfully connected to Tor control port {self.control_port}")
            return True
            
        except MissingPassword:
            self.logger.error("Tor control port requires a password")
            return False
        except IncorrectPassword:
            self.logger.error("Incorrect Tor control password")
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to Tor control port: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close connection to Tor control port."""
        if self.controller:
            try:
                self.controller.close()
                self.logger.info("Disconnected from Tor control port")
            except Exception as e:
                self.logger.error(f"Error disconnecting from Tor: {e}")
            finally:
                self.controller = None
    
    def new_circuit(self) -> bool:
        """
        Request a new Tor circuit (NEWNYM signal).
        
        Returns:
            bool: True if circuit renewal successful, False otherwise
        """
        if not self.controller:
            self.logger.error("Not connected to Tor control port")
            return False
            
        try:
            # Check if enough time has passed since last circuit change
            current_time = time.time()
            if current_time - self.last_circuit_time < 10:  # 10 second minimum between changes
                self.logger.warning("Circuit change requested too soon, waiting...")
                time.sleep(10 - (current_time - self.last_circuit_time))
            
            # Send NEWNYM signal to get new circuit
            self.controller.signal(Signal.NEWNYM)
            self.circuit_count += 1
            self.last_circuit_time = time.time()
            
            self.logger.info(f"New Tor circuit established (Circuit #{self.circuit_count})")
            
            # Wait for circuit to be built
            time.sleep(5)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to establish new Tor circuit: {e}")
            return False
    
    def get_circuit_info(self) -> Dict[str, Any]:
        """
        Get information about current Tor circuits.
        
        Returns:
            Dict[str, Any]: Circuit information or empty dict if unavailable
        """
        if not self.controller:
            return {}
            
        try:
            circuits = self.controller.get_circuits()
            if circuits:
                active_circuits = [c for c in circuits if c.status == 'BUILT']
                return {
                    'total_circuits': len(circuits),
                    'active_circuits': len(active_circuits),
                    'circuit_count': self.circuit_count
                }
        except Exception as e:
            self.logger.error(f"Failed to get circuit info: {e}")
            
        return {}
    
    def is_connected(self) -> bool:
        """
        Check if connected to Tor control port.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.controller:
            return False
            
        try:
            # Test connection by getting version
            self.controller.get_version()
            return True
        except Exception:
            return False
    
    def get_tor_info(self) -> Dict[str, str]:
        """
        Get Tor daemon information.
        
        Returns:
            Dict[str, str]: Tor version and status information
        """
        if not self.controller:
            return {'status': 'disconnected'}
            
        try:
            version = self.controller.get_version()
            return {
                'status': 'connected',
                'version': str(version),
                'circuits_created': str(self.circuit_count)
            }
        except Exception as e:
            self.logger.error(f"Failed to get Tor info: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def __enter__(self):
        """Context manager entry."""
        if self.connect():
            return self
        else:
            raise ConnectionError("Failed to connect to Tor control port")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
