"""
SICK PLOC 2D Vision Controller

This module provides a Python interface for communicating with SICK PLOC 2D Vision Systems
via TCP/IP socket connections. The VisionController class handles all communication protocols
and provides methods for executing vision jobs and retrieving part location data.

Author: Mecademic Integration Team
Version: 1.0
Compatible with: SICK PLOC2D 4.1+, Python 3.7+
"""

import socket
import time
import sys
from typing import List, Tuple, Optional, Dict, Any


class VisionController:
    """
    TCP/IP Communication interface for SICK PLOC 2D Vision System.
    
    This class provides methods for connecting to the PLOC 2D system, executing vision jobs,
    and retrieving part location and orientation data. It handles socket communication,
    error management, and data parsing.
    
    Attributes:
        ip_address (str): IP address of the PLOC 2D system
        port (int): TCP port for communication (default: system dependent)
        timeout (float): Socket timeout in seconds
        socket (socket.socket): TCP socket connection
        connected (bool): Connection status flag
        debug (bool): Enable debug output for troubleshooting
    """
    
    def __init__(self, ip_address: str, port: int = 2005, timeout: float = 5.0, debug: bool = False):
        """
        Initialize VisionController with network parameters.
        
        Args:
            ip_address (str): IP address of the SICK PLOC 2D system
            port (int): TCP port for communication (default: 2005)
            timeout (float): Socket timeout in seconds (default: 5.0)
            debug (bool): Enable debug output (default: False)
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.connected = False
        self.debug = debug
        
        if self.debug:
            print(f"VisionController initialized for {ip_address}:{port}")
    
    def connect(self) -> bool:
        """
        Establish TCP connection to the SICK PLOC 2D system.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            if self.connected:
                self.disconnect()
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip_address, self.port))
            self.connected = True
            
            if self.debug:
                print(f"Connected to PLOC 2D at {self.ip_address}:{self.port}")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """
        Close TCP connection to the SICK PLOC 2D system.
        """
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
            self.connected = False
            
            if self.debug:
                print("Disconnected from PLOC 2D")
                
        except Exception as e:
            if self.debug:
                print(f"Disconnect error: {e}")
    
    def _send_command(self, command: str) -> Optional[str]:
        """
        Send command to PLOC 2D system and receive response.
        
        Args:
            command (str): Command string to send
            
        Returns:
            Optional[str]: Response string from system, None if failed
        """
        if not self.connected:
            if self.debug:
                print("Not connected to PLOC 2D system")
            return None
        
        try:
            # Send command
            command_bytes = command.encode('utf-8') + b'\r\n'
            self.socket.send(command_bytes)
            
            if self.debug:
                print(f"Sent command: {command}")
            
            # Receive response
            response = self.socket.recv(1024).decode('utf-8').strip()
            
            if self.debug:
                print(f"Received response: {response}")
            
            return response
            
        except Exception as e:
            if self.debug:
                print(f"Command send/receive error: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status information from PLOC 2D.
        
        Returns:
            Dict[str, Any]: Status information including error codes and system state
        """
        status = {
            'connected': self.connected,
            'error_code': None,
            'system_ready': False,
            'last_job_result': None
        }
        
        if not self.connected:
            return status
        
        try:
            # Request system status (implementation depends on PLOC 2D protocol)
            response = self._send_command("STATUS")
            if response:
                # Parse response based on PLOC 2D protocol
                status['system_ready'] = True
                status['last_job_result'] = response
                
        except Exception as e:
            if self.debug:
                print(f"Status check error: {e}")
            status['error_code'] = str(e)
        
        return status
    
    def locate(self, job_id: int = 1) -> Optional[List[Dict[str, float]]]:
        """
        Execute vision job and return all detected parts.
        
        Args:
            job_id (int): Vision job ID to execute (default: 1)
            
        Returns:
            Optional[List[Dict[str, float]]]: List of detected parts with coordinates
                Each part dict contains: {'x': float, 'y': float, 'z': float, 'rz': float}
                Returns None if job execution failed
        """
        if not self.connected:
            if self.debug:
                print("Not connected to PLOC 2D system")
            return None
        
        try:
            # Execute vision job
            command = f"LOCATE {job_id}"
            response = self._send_command(command)
            
            if response is None:
                return None
            
            # Parse response to extract part coordinates
            parts = self._parse_locate_response(response)
            
            if self.debug:
                print(f"Located {len(parts)} parts")
            
            return parts
            
        except Exception as e:
            if self.debug:
                print(f"Locate operation error: {e}")
            return None
    
    def locate_by_index(self, job_id: int, part_index: int) -> Optional[Dict[str, float]]:
        """
        Get specific part data by index from vision job results.
        
        Args:
            job_id (int): Vision job ID
            part_index (int): Index of part to retrieve (1-based)
            
        Returns:
            Optional[Dict[str, float]]: Part coordinates and orientation
                Dict contains: {'x': float, 'y': float, 'z': float, 'rz': float}
                Returns None if part not found or job failed
        """
        if not self.connected:
            if self.debug:
                print("Not connected to PLOC 2D system")
            return None
        
        try:
            # Get specific part by index
            command = f"GET_PART {job_id} {part_index}"
            response = self._send_command(command)
            
            if response is None:
                return None
            
            # Parse single part response
            part_data = self._parse_part_response(response)
            
            if self.debug and part_data:
                print(f"Part {part_index}: x={part_data['x']:.2f}, y={part_data['y']:.2f}, rz={part_data['rz']:.2f}")
            
            return part_data
            
        except Exception as e:
            if self.debug:
                print(f"Locate by index error: {e}")
            return None
    
    def get_part_count(self, job_id: int) -> Optional[int]:
        """
        Get number of parts detected in the last vision job execution.
        
        Args:
            job_id (int): Vision job ID to query
            
        Returns:
            Optional[int]: Number of detected parts, None if query failed
        """
        if not self.connected:
            if self.debug:
                print("Not connected to PLOC 2D system")
            return None
        
        try:
            command = f"COUNT {job_id}"
            response = self._send_command(command)
            
            if response is None:
                return None
            
            # Parse count from response
            try:
                count = int(response.split()[-1])  # Assume count is last number in response
                if self.debug:
                    print(f"Part count for job {job_id}: {count}")
                return count
            except (ValueError, IndexError):
                if self.debug:
                    print(f"Could not parse count from response: {response}")
                return None
                
        except Exception as e:
            if self.debug:
                print(f"Get count error: {e}")
            return None
    
    def _parse_locate_response(self, response: str) -> List[Dict[str, float]]:
        """
        Parse LOCATE command response to extract part coordinates.
        
        Args:
            response (str): Raw response from PLOC 2D system
            
        Returns:
            List[Dict[str, float]]: List of part coordinate dictionaries
        """
        parts = []
        
        try:
            # Example parsing - actual format depends on PLOC 2D protocol
            lines = response.strip().split('\n')
            
            for line in lines:
                if line.startswith('PART'):
                    # Parse part data: "PART 1: X=100.5 Y=200.3 Z=0.0 RZ=45.2"
                    parts_data = line.split(':')[1].strip()
                    coords = {}
                    
                    for coord in parts_data.split():
                        if '=' in coord:
                            key, value = coord.split('=')
                            coords[key.lower()] = float(value)
                    
                    if 'x' in coords and 'y' in coords:
                        part = {
                            'x': coords.get('x', 0.0),
                            'y': coords.get('y', 0.0),
                            'z': coords.get('z', 0.0),
                            'rz': coords.get('rz', 0.0)
                        }
                        parts.append(part)
                        
        except Exception as e:
            if self.debug:
                print(f"Parse error: {e}")
        
        return parts
    
    def _parse_part_response(self, response: str) -> Optional[Dict[str, float]]:
        """
        Parse single part response to extract coordinates.
        
        Args:
            response (str): Raw response from PLOC 2D system
            
        Returns:
            Optional[Dict[str, float]]: Part coordinates, None if parsing failed
        """
        try:
            # Example parsing for single part response
            if 'X=' in response and 'Y=' in response:
                coords = {}
                
                for coord in response.split():
                    if '=' in coord:
                        key, value = coord.split('=')
                        coords[key.lower()] = float(value)
                
                return {
                    'x': coords.get('x', 0.0),
                    'y': coords.get('y', 0.0),
                    'z': coords.get('z', 0.0),
                    'rz': coords.get('rz', 0.0)
                }
                
        except Exception as e:
            if self.debug:
                print(f"Parse part response error: {e}")
        
        return None
    
    def set_job_parameters(self, job_id: int, parameters: Dict[str, Any]) -> bool:
        """
        Configure vision job parameters.
        
        Args:
            job_id (int): Vision job ID to configure
            parameters (Dict[str, Any]): Job parameters to set
            
        Returns:
            bool: True if configuration successful, False otherwise
        """
        if not self.connected:
            if self.debug:
                print("Not connected to PLOC 2D system")
            return False
        
        try:
            # Implementation depends on PLOC 2D configuration protocol
            for param, value in parameters.items():
                command = f"SET_PARAM {job_id} {param} {value}"
                response = self._send_command(command)
                
                if response is None or "ERROR" in response.upper():
                    if self.debug:
                        print(f"Failed to set parameter {param}={value}")
                    return False
            
            if self.debug:
                print(f"Job {job_id} parameters configured successfully")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"Set parameters error: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Destructor to ensure socket cleanup."""
        try:
            self.disconnect()
        except:
            pass


# Example usage and testing functions
def test_vision_controller(ip_address: str = "192.168.0.1"):
    """
    Test function demonstrating VisionController usage.
    
    Args:
        ip_address (str): IP address of PLOC 2D system
    """
    print(f"Testing VisionController with {ip_address}")
    
    # Create controller instance
    vision = VisionController(ip_address, debug=True)
    
    try:
        # Test connection
        if not vision.connect():
            print("Failed to connect to vision system")
            return
        
        # Test system status
        status = vision.get_system_status()
        print(f"System status: {status}")
        
        # Test part location
        parts = vision.locate(job_id=1)
        if parts:
            print(f"Found {len(parts)} parts:")
            for i, part in enumerate(parts, 1):
                print(f"  Part {i}: x={part['x']:.2f}, y={part['y']:.2f}, rz={part['rz']:.2f}")
        else:
            print("No parts found or locate failed")
        
        # Test part count
        count = vision.get_part_count(1)
        print(f"Part count: {count}")
        
        # Test specific part retrieval
        if count and count > 0:
            first_part = vision.locate_by_index(1, 1)
            if first_part:
                print(f"First part details: {first_part}")
        
    finally:
        vision.disconnect()


if __name__ == "__main__":
    # Run test if script is executed directly
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SICK PLOC 2D Vision Controller')
    parser.add_argument('--ip', default='192.168.0.1', help='IP address of PLOC 2D system')
    
    args = parser.parse_args()
    test_vision_controller(args.ip)