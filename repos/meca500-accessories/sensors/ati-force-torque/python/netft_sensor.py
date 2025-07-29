"""
NetFT Sensor Interface for ATI Force/Torque Sensors

This module provides a Python class interface for communicating with ATI Force/Torque
sensors using the NetFT UDP protocol. Supports real-time data streaming, sensor
configuration, and bias removal.

Compatible with:
- ATI Mini40 Net F/T sensors
- ATI Delta series sensors
- Other ATI sensors with NetFT interface

Author: Mecademic Integration Team
Version: 2.0
Updated: 2024
"""

import socket
import struct
import time
import threading
from typing import List, Tuple, Optional


class NetFTSensor:
    """
    ATI NetFT Sensor interface class for UDP communication.
    
    Provides methods for connecting to ATI Force/Torque sensors,
    streaming real-time data, and performing sensor operations.
    """
    
    def __init__(self, sensor_ip: str, sensor_port: int = 49152, timeout: float = 1.0):
        """
        Initialize NetFT sensor connection.
        
        Args:
            sensor_ip (str): IP address of the ATI sensor
            sensor_port (int): UDP port for sensor communication (default: 49152)
            timeout (float): Socket timeout in seconds (default: 1.0)
        """
        self.sensor_ip = sensor_ip
        self.sensor_port = sensor_port
        self.timeout = timeout
        
        # Socket for UDP communication
        self.socket = None
        
        # Data streaming control
        self.streaming = False
        self.stream_thread = None
        
        # Force/torque data storage
        self.current_data = [0.0] * 6  # [Fx, Fy, Fz, Tx, Ty, Tz]
        self.data_lock = threading.Lock()
        
        # Sensor configuration
        self.sample_rate = 1000  # Default 1 kHz
        self.bias_vector = [0.0] * 6
        
        # Data conversion factors (sensor specific)
        self.force_scale = 1.0  # Scale factor for forces (N)
        self.torque_scale = 1.0  # Scale factor for torques (Nm)
        
    def connect(self) -> bool:
        """
        Establish UDP connection to the sensor.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            
            # Test connection by requesting sensor information
            if self._test_connection():
                print(f"Successfully connected to ATI sensor at {self.sensor_ip}:{self.sensor_port}")
                return True
            else:
                print("Failed to establish communication with sensor")
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """
        Close the sensor connection and stop data streaming.
        """
        self.stop_streaming()
        
        if self.socket:
            self.socket.close()
            self.socket = None
            print("Disconnected from ATI sensor")
    
    def _test_connection(self) -> bool:
        """
        Test the connection by sending a status request.
        
        Returns:
            bool: True if sensor responds, False otherwise
        """
        try:
            # Send status request command
            command = self._create_command(0x0000)  # Status request
            self.socket.sendto(command, (self.sensor_ip, self.sensor_port))
            
            # Wait for response
            response, addr = self.socket.recvfrom(1024)
            return len(response) > 0
            
        except socket.timeout:
            return False
        except Exception:
            return False
    
    def start_streaming(self, sample_rate: int = 1000) -> bool:
        """
        Start real-time data streaming from the sensor.
        
        Args:
            sample_rate (int): Desired sample rate in Hz (default: 1000)
            
        Returns:
            bool: True if streaming started successfully
        """
        if self.streaming:
            print("Data streaming already active")
            return True
            
        try:
            self.sample_rate = sample_rate
            
            # Send start streaming command
            command = self._create_streaming_command(sample_rate)
            self.socket.sendto(command, (self.sensor_ip, self.sensor_port))
            
            # Start streaming thread
            self.streaming = True
            self.stream_thread = threading.Thread(target=self._stream_data)
            self.stream_thread.daemon = True
            self.stream_thread.start()
            
            print(f"Started data streaming at {sample_rate} Hz")
            return True
            
        except Exception as e:
            print(f"Failed to start streaming: {e}")
            return False
    
    def stop_streaming(self):
        """
        Stop real-time data streaming.
        """
        if self.streaming:
            self.streaming = False
            
            # Send stop streaming command
            try:
                command = self._create_command(0x0001)  # Stop streaming
                self.socket.sendto(command, (self.sensor_ip, self.sensor_port))
            except:
                pass
            
            # Wait for thread to finish
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=2.0)
            
            print("Stopped data streaming")
    
    def _stream_data(self):
        """
        Internal method for continuous data streaming.
        Runs in separate thread to maintain real-time performance.
        """
        while self.streaming:
            try:
                # Receive data packet
                data, addr = self.socket.recvfrom(1024)
                
                # Parse force/torque data
                force_torque = self._parse_data_packet(data)
                
                if force_torque:
                    # Update current data with thread safety
                    with self.data_lock:
                        self.current_data = force_torque
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self.streaming:  # Only print error if still streaming
                    print(f"Data streaming error: {e}")
                break
    
    def get_force(self) -> List[float]:
        """
        Get the current force/torque readings.
        
        Returns:
            List[float]: [Fx, Fy, Fz, Tx, Ty, Tz] in N and Nm
        """
        with self.data_lock:
            # Apply bias correction
            corrected_data = [
                self.current_data[i] - self.bias_vector[i] 
                for i in range(6)
            ]
            return corrected_data.copy()
    
    def get_force_xyz(self) -> Tuple[float, float, float]:
        """
        Get current force readings for X, Y, Z axes.
        
        Returns:
            Tuple[float, float, float]: (Fx, Fy, Fz) in Newtons
        """
        force_data = self.get_force()
        return force_data[0], force_data[1], force_data[2]
    
    def get_torque_xyz(self) -> Tuple[float, float, float]:
        """
        Get current torque readings for X, Y, Z axes.
        
        Returns:
            Tuple[float, float, float]: (Tx, Ty, Tz) in Newton-meters
        """
        force_data = self.get_force()
        return force_data[3], force_data[4], force_data[5]
    
    def set_bias(self, samples: int = 100) -> bool:
        """
        Set the current sensor readings as bias/zero reference.
        
        Args:
            samples (int): Number of samples to average for bias calculation
            
        Returns:
            bool: True if bias set successfully
        """
        if not self.streaming:
            print("Data streaming must be active to set bias")
            return False
        
        try:
            print(f"Collecting {samples} samples for bias calculation...")
            
            # Collect samples
            bias_samples = []
            for i in range(samples):
                with self.data_lock:
                    bias_samples.append(self.current_data.copy())
                time.sleep(0.001)  # 1ms delay between samples
            
            # Calculate average
            self.bias_vector = [
                sum(sample[i] for sample in bias_samples) / len(bias_samples)
                for i in range(6)
            ]
            
            print("Bias vector set successfully:")
            print(f"  Forces: Fx={self.bias_vector[0]:.3f}, Fy={self.bias_vector[1]:.3f}, Fz={self.bias_vector[2]:.3f}")
            print(f"  Torques: Tx={self.bias_vector[3]:.3f}, Ty={self.bias_vector[4]:.3f}, Tz={self.bias_vector[5]:.3f}")
            
            return True
            
        except Exception as e:
            print(f"Failed to set bias: {e}")
            return False
    
    def clear_bias(self):
        """
        Clear the current bias vector (reset to zero).
        """
        self.bias_vector = [0.0] * 6
        print("Bias vector cleared")
    
    def _create_command(self, command_code: int) -> bytes:
        """
        Create a NetFT command packet.
        
        Args:
            command_code (int): Command code for the operation
            
        Returns:
            bytes: Formatted command packet
        """
        # NetFT command packet format: [header][command][sequence][payload]
        header = 0x1234  # Standard NetFT header
        sequence = 0x0001  # Sequence number
        
        # Pack command as binary data
        packet = struct.pack('>HHH', header, command_code, sequence)
        return packet
    
    def _create_streaming_command(self, sample_rate: int) -> bytes:
        """
        Create a streaming start command with specified sample rate.
        
        Args:
            sample_rate (int): Desired sample rate in Hz
            
        Returns:
            bytes: Formatted streaming command
        """
        # Command to start streaming with sample rate
        header = 0x1234
        command = 0x0002  # Start streaming command
        sequence = 0x0001
        rate_code = self._sample_rate_to_code(sample_rate)
        
        packet = struct.pack('>HHHH', header, command, sequence, rate_code)
        return packet
    
    def _sample_rate_to_code(self, rate: int) -> int:
        """
        Convert sample rate to NetFT rate code.
        
        Args:
            rate (int): Sample rate in Hz
            
        Returns:
            int: NetFT rate code
        """
        rate_map = {
            1: 0x0001,      # 1 Hz
            10: 0x000A,     # 10 Hz
            100: 0x0064,    # 100 Hz
            500: 0x01F4,    # 500 Hz
            1000: 0x03E8,   # 1000 Hz
            2000: 0x07D0,   # 2000 Hz
            7000: 0x1B58    # 7000 Hz
        }
        return rate_map.get(rate, 0x03E8)  # Default to 1000 Hz
    
    def _parse_data_packet(self, data: bytes) -> Optional[List[float]]:
        """
        Parse a data packet from the sensor.
        
        Args:
            data (bytes): Raw data packet from sensor
            
        Returns:
            Optional[List[float]]: Parsed force/torque data or None if invalid
        """
        try:
            # NetFT data packet format: header + sequence + status + force/torque data
            if len(data) < 36:  # Minimum packet size
                return None
            
            # Unpack header and check validity
            header, sequence, status = struct.unpack('>HHI', data[:8])
            
            if header != 0x1234:  # Invalid header
                return None
            
            # Unpack force/torque data (6 int32 values)
            force_torque_raw = struct.unpack('>6i', data[8:32])
            
            # Convert to physical units (sensor specific scaling)
            force_torque = [
                force_torque_raw[0] * self.force_scale,   # Fx
                force_torque_raw[1] * self.force_scale,   # Fy  
                force_torque_raw[2] * self.force_scale,   # Fz
                force_torque_raw[3] * self.torque_scale,  # Tx
                force_torque_raw[4] * self.torque_scale,  # Ty
                force_torque_raw[5] * self.torque_scale   # Tz
            ]
            
            return force_torque
            
        except Exception:
            return None
    
    def get_sensor_info(self) -> dict:
        """
        Get sensor information and status.
        
        Returns:
            dict: Sensor information including model, serial number, etc.
        """
        info = {
            'ip_address': self.sensor_ip,
            'port': self.sensor_port,
            'sample_rate': self.sample_rate,
            'streaming': self.streaming,
            'connected': self.socket is not None,
            'bias_set': any(abs(b) > 0.001 for b in self.bias_vector)
        }
        return info
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Example usage and testing functions
def test_sensor_connection():
    """Test basic sensor connection and data reading."""
    sensor_ip = "192.168.1.100"  # Replace with your sensor IP
    
    print("Testing ATI NetFT sensor connection...")
    
    with NetFTSensor(sensor_ip) as sensor:
        if sensor.connect():
            print("✓ Connection successful")
            
            # Start streaming
            if sensor.start_streaming(1000):
                print("✓ Data streaming started")
                
                # Set bias
                time.sleep(1)  # Allow data to stabilize
                sensor.set_bias()
                
                # Read data for 5 seconds
                print("\nReading force/torque data for 5 seconds...")
                start_time = time.time()
                
                while time.time() - start_time < 5.0:
                    force_data = sensor.get_force()
                    print(f"F: [{force_data[0]:6.2f}, {force_data[1]:6.2f}, {force_data[2]:6.2f}] "
                          f"T: [{force_data[3]:6.3f}, {force_data[4]:6.3f}, {force_data[5]:6.3f}]", 
                          end='\r')
                    time.sleep(0.1)
                
                print("\n✓ Data reading completed")
                
            else:
                print("✗ Failed to start streaming")
        else:
            print("✗ Connection failed")


if __name__ == "__main__":
    test_sensor_connection()