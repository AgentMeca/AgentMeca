# ATI Delta IP60 Force/Torque Sensor Integration

Integration system for connecting ATI Delta NET F/T transducers with IP60 protection to Mecademic Meca500 robots. Provides high-precision 6-axis force/torque sensing for demanding industrial applications including product testing, assembly operations, and collaborative robotics.

This repository provides complete integration documentation for:
- **ATI Delta NET F/T Transducer**: Professional-grade 6-axis force/torque sensor
- **IP60 Protection Rating**: Industrial-grade environmental protection
- **NetBox Integration**: High-speed Ethernet interface for large transducers
- **Custom Mounting Solutions**: 3D-printed brackets and mechanical adapters

## System Overview

### Components Required

#### Hardware Components
- **Robot**: Meca500 robot (firmware v8.1.6 or higher)
- **Sensor**: ATI Delta NET F/T Transducer with IP60 protection
- **Interface**: NetBox for large transducers (ATI NetBox)
- **Mounting**: Custom 3D-printed mounting bracket
- **Hardware**: M6 x 1.0 screws and nuts for mounting
- **Test Load**: 500g payload for testing and validation
- **Network**: Ethernet cable for sensor communication

#### Software Components
- **ATI NetFT Software**: Official ATI sensor interface applications
- **Mecademic Python API**: Robot control and integration
- **FT Data Viewer**: Real-time force/torque data visualization
- **Calibration Software**: Sensor calibration and configuration tools

## Sensor Specifications

### ATI Delta Specifications
| Parameter | Value | Unit |
|-----------|-------|------|
| **Force Range Fxy** | ±660 | N |
| **Force Range Fz** | ±1980 | N |
| **Torque Range Txy** | ±60 | Nm |
| **Torque Range Tz** | ±60 | Nm |
| **Weight** | 0.913 | kg |
| **Diameter** | 117 | mm |
| **Height** | 33.3 | mm |
| **Protection Rating** | IP60 | - |
| **Communication** | Ethernet | UDP/TCP |
| **Data Rate** | Up to 7000 | Hz |
| **Resolution** | 1/12800 | of full scale |

### Environmental Specifications
- **Operating Temperature**: -25°C to +85°C
- **Storage Temperature**: -40°C to +100°C
- **Shock Rating**: 100g for 11ms
- **Vibration Rating**: 10g RMS, 5-2000 Hz
- **EMI/EMC Compliance**: CE certified
- **Material**: Aluminum alloy with protective coating

### Communication Interface
- **Protocol**: NetFT over Ethernet
- **Default IP**: 192.168.1.1 (configurable)
- **Port**: 49152 (UDP), 49151 (TCP)
- **Packet Rate**: Configurable 1-7000 Hz
- **Latency**: < 1ms at maximum data rate
- **Network**: 10/100/1000 Mbps Ethernet

## Mechanical Integration

### Mounting Configuration

#### Robot-Mounted Configuration
In this configuration, the Delta sensor is mounted between the robot flange and end-effector:

```
Meca500 Flange → Custom Bracket → ATI Delta → End-Effector
```

**Advantages:**
- Direct force measurement at tool interface
- Compact installation
- Real-time force feedback for robot control

**Considerations:**
- Additional mass affects robot dynamics
- Reduced payload capacity
- Tool transformation required for force vectors

#### Work Surface Configuration
Alternative mounting with sensor on work surface:

```
Work Surface → ATI Delta → Custom Bracket → Test Fixture
```

**Advantages:**
- No impact on robot payload
- Larger force measurement range
- Easier sensor access for maintenance

**Considerations:**
- Fixed measurement location
- Coordinate transformation required
- Additional workspace setup

### Custom Mounting Bracket

#### 3D-Printed Bracket Specifications
- **Material**: High-strength engineering plastic (PLA+, PETG, or ABS)
- **Mounting Pattern**: Compatible with Meca500 flange (ISO 9409-1-50-4-M6)
- **Sensor Interface**: M6 x 1.0 threaded holes for Delta mounting
- **Tool Offset**: 12.5mm Z-axis offset for tool transformation
- **Safety Factor**: 3:1 minimum for expected loads

#### Bracket Dimensions
```
Flange Interface:
- Bolt Circle Diameter: 40mm
- Bolt Pattern: 4 x M6 holes
- Flange Thickness: 10mm

Sensor Interface:
- Mounting Pattern: ATI Delta standard
- Thread: M6 x 1.0
- Depth: 15mm minimum thread engagement
```

#### Installation Instructions
1. **Print Bracket**: Use high-quality 3D printer with engineering materials
2. **Post-Processing**: Remove support material and smooth mounting surfaces
3. **Thread Preparation**: Tap M6 holes if required for threaded inserts
4. **Test Fit**: Verify fit with robot flange and sensor before final assembly
5. **Torque Specification**: Apply proper torque values for all fasteners

## Installation Guide

### 1. Mechanical Installation

#### Sensor Mounting
1. **Position Sensor**: Mount ATI Delta on work surface or custom fixture
2. **Attach Bracket**: Secure custom 3D-printed bracket to sensor using M6 screws
3. **Robot Connection**: Mount Meca500 to bracket using flange bolts
4. **Alignment**: Verify proper alignment and tool offset measurements
5. **Cable Routing**: Route sensor cable with appropriate strain relief

#### NetBox Setup
1. **NetBox Placement**: Install NetBox in accessible location near sensor
2. **Power Connection**: Connect NetBox to appropriate power supply
3. **Sensor Cable**: Connect Delta sensor to NetBox using provided cable
4. **Network Cable**: Connect NetBox to network switch or directly to PC
5. **Status Verification**: Check NetBox status LEDs for proper operation

### 2. Network Configuration

#### IP Address Setup
```python
# Default sensor network configuration
SENSOR_IP = "192.168.1.1"      # Default Delta IP address
NETBOX_IP = "192.168.1.100"    # NetBox IP (configurable)
PC_IP = "192.168.1.50"         # PC IP address
SUBNET_MASK = "255.255.255.0"  # Network subnet mask
```

#### Network Interface Configuration
1. **Configure PC Network**: Set static IP in sensor subnet
2. **Test Connectivity**: Ping sensor to verify network communication
3. **Firewall Settings**: Allow UDP traffic on port 49152
4. **Router Configuration**: Configure port forwarding if using router

### 3. Software Installation

#### ATI Software Installation
1. **Download Software**: Get latest ATI NetFT software from ATI website
2. **Install Applications**: Install NetFT Utility and Java applications
3. **Driver Installation**: Install network drivers if required
4. **License Activation**: Activate software licenses if applicable

#### Python Dependencies
```bash
pip install mecademicpy numpy matplotlib socket struct
```

### 4. Sensor Configuration

#### Initial Calibration
1. **Factory Reset**: Reset sensor to factory default settings
2. **Load Calibration**: Import factory calibration matrix
3. **Coordinate Frame**: Configure tool coordinate system
4. **Bias Removal**: Perform initial bias calibration with no load

#### Tool Transformation
```python
# Tool transformation for 12.5mm Z-offset bracket
TOOL_TRANSFORM = {
    'translation': [0.0, 0.0, 12.5],  # mm offset in Z
    'rotation': [0.0, 0.0, 0.0]       # No rotation
}

def apply_tool_transform(force_data, transform):
    """Apply tool coordinate transformation to force data"""
    # Transform force vector from sensor to tool coordinates
    # Account for mounting offset and orientation
    
    transformed_force = force_data.copy()
    
    # Apply translation offset (affects torque measurements)
    dx, dy, dz = transform['translation']
    
    # Adjust torques for offset
    transformed_force[3] += force_data[1] * dz - force_data[2] * dy  # Tx
    transformed_force[4] += force_data[2] * dx - force_data[0] * dz  # Ty
    transformed_force[5] += force_data[0] * dy - force_data[1] * dx  # Tz
    
    return transformed_force
```

## Programming Interface

### Python Integration

#### Basic Sensor Interface
```python
import socket
import struct
import time
from typing import List, Tuple

class ATIDeltaSensor:
    """
    ATI Delta NET F/T sensor interface for high-precision force measurement.
    
    Provides UDP communication with ATI Delta sensors through NetBox
    interface, supporting high-speed data acquisition and real-time control.
    """
    
    def __init__(self, sensor_ip: str = "192.168.1.1", port: int = 49152):
        self.sensor_ip = sensor_ip
        self.port = port
        self.socket = None
        self.connected = False
        
        # Calibration matrix (loaded from sensor)
        self.calibration_matrix = None
        self.bias_vector = [0.0] * 6
        
        # Delta-specific scaling factors
        self.force_scale = 1.0 / 1000000.0  # Convert to Newtons
        self.torque_scale = 1.0 / 1000000.0  # Convert to Newton-meters
    
    def connect(self) -> bool:
        """Establish connection to ATI Delta sensor."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)
            
            # Test connection
            if self._test_communication():
                self.connected = True
                print(f"Connected to ATI Delta at {self.sensor_ip}")
                return True
            else:
                print("Failed to communicate with sensor")
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def _test_communication(self) -> bool:
        """Test sensor communication."""
        try:
            # Send status request
            request = struct.pack('>HH', 0x1234, 0x0000)
            self.socket.sendto(request, (self.sensor_ip, self.port))
            
            # Wait for response
            response, addr = self.socket.recvfrom(1024)
            return len(response) > 0
            
        except:
            return False
    
    def read_force_single(self) -> List[float]:
        """Read single force/torque measurement."""
        try:
            # Request data packet
            request = struct.pack('>HH', 0x1234, 0x0002)
            self.socket.sendto(request, (self.sensor_ip, self.port))
            
            # Receive response
            response, addr = self.socket.recvfrom(1024)
            
            # Parse force/torque data
            force_data = self._parse_response(response)
            
            # Apply bias correction
            corrected_data = [
                force_data[i] - self.bias_vector[i] 
                for i in range(6)
            ]
            
            return corrected_data
            
        except Exception as e:
            print(f"Read error: {e}")
            return [0.0] * 6
    
    def _parse_response(self, response: bytes) -> List[float]:
        """Parse sensor response packet."""
        if len(response) < 36:
            return [0.0] * 6
        
        # Unpack header and data
        header, sequence, status = struct.unpack('>HHI', response[:8])
        force_raw = struct.unpack('>6i', response[8:32])
        
        # Convert to physical units
        force_data = [
            force_raw[0] * self.force_scale,   # Fx
            force_raw[1] * self.force_scale,   # Fy
            force_raw[2] * self.force_scale,   # Fz
            force_raw[3] * self.torque_scale,  # Tx
            force_raw[4] * self.torque_scale,  # Ty
            force_raw[5] * self.torque_scale   # Tz
        ]
        
        return force_data
    
    def set_bias(self, samples: int = 100):
        """Set bias using current sensor readings."""
        print(f"Setting bias using {samples} samples...")
        
        bias_samples = []
        for i in range(samples):
            force_data = self.read_force_single()
            bias_samples.append(force_data)
            time.sleep(0.01)
        
        # Calculate average bias
        self.bias_vector = [
            sum(sample[i] for sample in bias_samples) / len(bias_samples)
            for i in range(6)
        ]
        
        print("Bias set successfully:")
        print(f"  Forces: Fx={self.bias_vector[0]:.3f}, Fy={self.bias_vector[1]:.3f}, Fz={self.bias_vector[2]:.3f}")
        print(f"  Torques: Tx={self.bias_vector[3]:.3f}, Ty={self.bias_vector[4]:.3f}, Tz={self.bias_vector[5]:.3f}")
    
    def disconnect(self):
        """Close sensor connection."""
        if self.socket:
            self.socket.close()
        self.connected = False
        print("Disconnected from ATI Delta sensor")
```

#### High-Speed Data Acquisition
```python
class DeltaDataLogger:
    """High-speed data logging for ATI Delta sensor."""
    
    def __init__(self, sensor: ATIDeltaSensor, log_file: str = None):
        self.sensor = sensor
        self.log_file = log_file or f"delta_data_{int(time.time())}.csv"
        self.logging = False
        self.data_buffer = []
    
    def start_logging(self, duration: float = 60.0, sample_rate: int = 1000):
        """Start high-speed data logging."""
        self.logging = True
        sample_interval = 1.0 / sample_rate
        
        print(f"Starting data logging at {sample_rate} Hz for {duration} seconds")
        
        with open(self.log_file, 'w') as f:
            # Write header
            f.write("Timestamp,Fx,Fy,Fz,Tx,Ty,Tz\n")
            
            start_time = time.time()
            next_sample_time = start_time
            
            while time.time() - start_time < duration and self.logging:
                current_time = time.time()
                
                if current_time >= next_sample_time:
                    # Read force data
                    force_data = self.sensor.read_force_single()
                    
                    # Write to file
                    f.write(f"{current_time:.6f},{','.join(f'{x:.6f}' for x in force_data)}\n")
                    
                    # Schedule next sample
                    next_sample_time += sample_interval
                
                # Small delay to prevent CPU overload
                time.sleep(0.0001)
        
        print(f"Data logging completed. File: {self.log_file}")
    
    def stop_logging(self):
        """Stop data logging."""
        self.logging = False
```

### Robot Integration Examples

#### Basic Force Monitoring
```python
from mecademicpy import Robot

def force_monitoring_demo():
    """Demonstrate basic force monitoring with robot motion."""
    
    # Initialize components
    robot = Robot()
    sensor = ATIDeltaSensor("192.168.1.1")
    
    # Connect to devices
    robot.Connect("192.168.0.100")
    robot.ActivateRobot()
    robot.Home()
    
    sensor.connect()
    sensor.set_bias()
    
    try:
        # Move to starting position
        robot.MovePose(200, 0, 200, 0, 90, 0)
        robot.WaitIdle()
        
        # Perform test movements while monitoring forces
        test_positions = [
            [220, 0, 200, 0, 90, 0],
            [200, 20, 200, 0, 90, 0],
            [180, 0, 200, 0, 90, 0],
            [200, -20, 200, 0, 90, 0],
            [200, 0, 200, 0, 90, 0]
        ]
        
        for position in test_positions:
            print(f"Moving to position: {position}")
            robot.MovePose(*position)
            
            # Monitor forces during movement
            while not robot.GetStatusRobot().idle:
                force_data = sensor.read_force_single()
                force_magnitude = sum(f*f for f in force_data[:3])**0.5
                
                print(f"Force magnitude: {force_magnitude:.2f} N", end='\r')
                
                # Safety check
                if force_magnitude > 50.0:
                    print("\nForce limit exceeded! Stopping robot.")
                    robot.PauseMotion()
                    break
                
                time.sleep(0.1)
            
            print("\nPosition reached")
            time.sleep(1)
    
    finally:
        robot.DeactivateRobot()
        robot.Disconnect()
        sensor.disconnect()
```

#### Force-Controlled Testing
```python
def product_testing_sequence():
    """Example product testing with force feedback."""
    
    robot = Robot()
    sensor = ATIDeltaSensor("192.168.1.1")
    
    # Test parameters
    test_force = 100.0  # N
    test_duration = 5.0  # seconds
    force_tolerance = 5.0  # N
    
    robot.Connect("192.168.0.100")
    robot.ActivateRobot()
    robot.Home()
    
    sensor.connect()
    sensor.set_bias()
    
    try:
        # Move to test position
        robot.MovePose(200, 0, 150, 0, 90, 0)  # Above test fixture
        robot.WaitIdle()
        
        # Approach test surface
        approach_complete = False
        while not approach_complete:
            robot.MoveLinRelTrf(0, 0, -1, 0, 0, 0)  # Move down 1mm
            robot.WaitIdle()
            
            force_data = sensor.read_force_single()
            current_force = abs(force_data[2])  # Z-axis force
            
            if current_force > 5.0:  # Contact detected
                approach_complete = True
                print("Contact with test surface detected")
        
        # Apply test force
        print(f"Applying test force: {test_force} N")
        
        test_start_time = time.time()
        force_readings = []
        
        while time.time() - test_start_time < test_duration:
            force_data = sensor.read_force_single()
            current_force = abs(force_data[2])
            force_readings.append(current_force)
            
            # Simple force control
            force_error = test_force - current_force
            
            if abs(force_error) > force_tolerance:
                # Adjust position to maintain force
                adjustment = force_error * 0.01  # Simple proportional control
                robot.MoveLinRelTrf(0, 0, adjustment, 0, 0, 0)
                robot.WaitIdle()
            
            print(f"Applied force: {current_force:.2f} N (target: {test_force:.2f} N)", end='\r')
            time.sleep(0.1)
        
        # Analyze test results
        avg_force = sum(force_readings) / len(force_readings)
        force_std = (sum((f - avg_force)**2 for f in force_readings) / len(force_readings))**0.5
        
        print(f"\nTest completed:")
        print(f"  Average force: {avg_force:.2f} N")
        print(f"  Standard deviation: {force_std:.2f} N")
        print(f"  Force stability: {'PASS' if force_std < force_tolerance else 'FAIL'}")
        
        # Return to safe position
        robot.MoveLinRelTrf(0, 0, 20, 0, 0, 0)  # Lift 20mm
        robot.WaitIdle()
    
    finally:
        robot.DeactivateRobot()
        robot.Disconnect()
        sensor.disconnect()
```

## Testing and Validation

### 500g Test Load Validation
```python
def validate_sensor_accuracy():
    """Validate sensor accuracy using 500g test weight."""
    
    sensor = ATIDeltaSensor("192.168.1.1")
    sensor.connect()
    
    # Expected force for 500g weight
    expected_force = 0.5 * 9.81  # 4.905 N
    tolerance = 0.1  # ±0.1 N tolerance
    
    print("Sensor accuracy validation:")
    print("1. Ensure sensor is horizontal with no load")
    print("2. Press Enter to set bias...")
    input()
    
    sensor.set_bias()
    
    print("3. Place 500g test weight on sensor")
    print("4. Press Enter to measure...")
    input()
    
    # Take multiple readings
    readings = []
    for i in range(50):
        force_data = sensor.read_force_single()
        readings.append(abs(force_data[2]))  # Z-axis force magnitude
        time.sleep(0.1)
    
    # Calculate statistics
    avg_force = sum(readings) / len(readings)
    min_force = min(readings)
    max_force = max(readings)
    std_force = (sum((f - avg_force)**2 for f in readings) / len(readings))**0.5
    
    # Validate accuracy
    accuracy_error = abs(avg_force - expected_force)
    accuracy_pass = accuracy_error <= tolerance
    
    print(f"\nValidation Results:")
    print(f"  Expected force: {expected_force:.3f} N")
    print(f"  Measured force: {avg_force:.3f} ± {std_force:.3f} N")
    print(f"  Range: {min_force:.3f} - {max_force:.3f} N")
    print(f"  Accuracy error: {accuracy_error:.3f} N")
    print(f"  Accuracy test: {'PASS' if accuracy_pass else 'FAIL'}")
    
    sensor.disconnect()
    return accuracy_pass
```

### Dynamic Response Testing
```python
def test_dynamic_response():
    """Test sensor dynamic response characteristics."""
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    sensor = ATIDeltaSensor("192.168.1.1")
    sensor.connect()
    sensor.set_bias()
    
    # Step response test
    print("Dynamic response test:")
    print("1. Apply sudden force/torque to sensor")
    print("2. Press Enter to start recording...")
    input()
    
    # Record high-speed data
    sample_rate = 1000  # Hz
    duration = 2.0  # seconds
    
    timestamps = []
    force_data = []
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        current_time = time.time()
        force_reading = sensor.read_force_single()
        
        timestamps.append(current_time - start_time)
        force_data.append(force_reading)
        
        time.sleep(1.0 / sample_rate)
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    labels = ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']
    units = ['N', 'N', 'N', 'Nm', 'Nm', 'Nm']
    
    for i in range(6):
        plt.subplot(2, 3, i+1)
        values = [reading[i] for reading in force_data]
        plt.plot(timestamps, values)
        plt.title(f'{labels[i]} ({units[i]})')
        plt.xlabel('Time (s)')
        plt.ylabel(f'Force/Torque ({units[i]})')
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('delta_dynamic_response.png')
    plt.show()
    
    sensor.disconnect()
```

## Advanced Applications

### Multi-Axis Force Control
```python
class MultiAxisForceController:
    """Advanced multi-axis force control for ATI Delta sensor."""
    
    def __init__(self, robot, sensor):
        self.robot = robot
        self.sensor = sensor
        
        # PID control parameters for each axis
        self.pid_params = {
            'Fx': {'kp': 0.1, 'ki': 0.01, 'kd': 0.05},
            'Fy': {'kp': 0.1, 'ki': 0.01, 'kd': 0.05},
            'Fz': {'kp': 0.2, 'ki': 0.02, 'kd': 0.08},
            'Tx': {'kp': 0.05, 'ki': 0.005, 'kd': 0.02},
            'Ty': {'kp': 0.05, 'ki': 0.005, 'kd': 0.02},
            'Tz': {'kp': 0.05, 'ki': 0.005, 'kd': 0.02}
        }
        
        # PID state variables
        self.error_integral = [0.0] * 6
        self.previous_error = [0.0] * 6
    
    def controlled_contact(self, target_forces: List[float], 
                         control_mask: List[bool] = None,
                         max_velocity: float = 5.0) -> bool:
        """
        Perform controlled contact with specified force/torque targets.
        
        Args:
            target_forces: Target [Fx, Fy, Fz, Tx, Ty, Tz] values
            control_mask: Boolean mask for controlled axes
            max_velocity: Maximum velocity for force control
        """
        
        if control_mask is None:
            control_mask = [True] * 6
        
        control_frequency = 100  # Hz
        control_duration = 10.0  # seconds
        
        start_time = time.time()
        
        while time.time() - start_time < control_duration:
            # Read current forces
            current_forces = self.sensor.read_force_single()
            
            # Calculate velocity corrections
            velocity_correction = [0.0] * 6
            
            for i in range(6):
                if control_mask[i]:
                    error = target_forces[i] - current_forces[i]
                    
                    # PID calculation
                    self.error_integral[i] += error
                    error_derivative = error - self.previous_error[i]
                    self.previous_error[i] = error
                    
                    params = list(self.pid_params.values())[i]
                    correction = (params['kp'] * error + 
                                params['ki'] * self.error_integral[i] +
                                params['kd'] * error_derivative)
                    
                    # Limit correction magnitude
                    correction = max(-max_velocity, min(max_velocity, correction))
                    velocity_correction[i] = correction
            
            # Apply velocity command
            self.robot.MoveVelTrf(velocity_correction)
            
            # Status display
            force_errors = [abs(target_forces[i] - current_forces[i]) for i in range(6)]
            max_error = max(force_errors)
            
            print(f"Max error: {max_error:.3f}, Current forces: {[f'{f:.2f}' for f in current_forces[:3]]}", end='\r')
            
            # Check convergence
            if max_error < 0.5:  # Converged within 0.5 N/Nm
                print("\nForce control converged")
                break
            
            time.sleep(1.0 / control_frequency)
        
        # Stop robot motion
        self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
        return True
```

### Data Analysis and Visualization
```python
import matplotlib.pyplot as plt
import numpy as np

def analyze_force_data(data_file: str):
    """Comprehensive analysis of logged force data."""
    
    # Load data
    data = np.loadtxt(data_file, delimiter=',', skiprows=1)
    timestamps = data[:, 0]
    forces = data[:, 1:4]  # Fx, Fy, Fz
    torques = data[:, 4:7]  # Tx, Ty, Tz
    
    # Calculate statistics
    force_magnitude = np.sqrt(np.sum(forces**2, axis=1))
    torque_magnitude = np.sqrt(np.sum(torques**2, axis=1))
    
    # Frequency analysis
    sample_rate = 1.0 / np.mean(np.diff(timestamps))
    frequencies = np.fft.fftfreq(len(force_magnitude), 1/sample_rate)
    force_fft = np.fft.fft(force_magnitude)
    
    # Create comprehensive plots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Time domain plots
    axes[0, 0].plot(timestamps, forces)
    axes[0, 0].set_title('Forces vs Time')
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Force (N)')
    axes[0, 0].legend(['Fx', 'Fy', 'Fz'])
    axes[0, 0].grid(True)
    
    axes[0, 1].plot(timestamps, torques)
    axes[0, 1].set_title('Torques vs Time')
    axes[0, 1].set_xlabel('Time (s)')
    axes[0, 1].set_ylabel('Torque (Nm)')
    axes[0, 1].legend(['Tx', 'Ty', 'Tz'])
    axes[0, 1].grid(True)
    
    axes[0, 2].plot(timestamps, force_magnitude)
    axes[0, 2].set_title('Force Magnitude')
    axes[0, 2].set_xlabel('Time (s)')
    axes[0, 2].set_ylabel('|F| (N)')
    axes[0, 2].grid(True)
    
    # Frequency domain analysis
    positive_freq_idx = frequencies > 0
    axes[1, 0].loglog(frequencies[positive_freq_idx], 
                      np.abs(force_fft[positive_freq_idx]))
    axes[1, 0].set_title('Force Spectrum')
    axes[1, 0].set_xlabel('Frequency (Hz)')
    axes[1, 0].set_ylabel('Magnitude')
    axes[1, 0].grid(True)
    
    # Statistics
    axes[1, 1].hist(force_magnitude, bins=50, alpha=0.7)
    axes[1, 1].set_title('Force Magnitude Distribution')
    axes[1, 1].set_xlabel('Force (N)')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].grid(True)
    
    # Force trajectory in 3D
    from mpl_toolkits.mplot3d import Axes3D
    axes[1, 2].remove()
    ax_3d = fig.add_subplot(2, 3, 6, projection='3d')
    ax_3d.plot(forces[:, 0], forces[:, 1], forces[:, 2])
    ax_3d.set_title('3D Force Trajectory')
    ax_3d.set_xlabel('Fx (N)')
    ax_3d.set_ylabel('Fy (N)')
    ax_3d.set_zlabel('Fz (N)')
    
    plt.tight_layout()
    plt.savefig('delta_analysis.png', dpi=300)
    plt.show()
    
    # Print summary statistics
    print("Force Data Analysis Summary:")
    print(f"  Duration: {timestamps[-1] - timestamps[0]:.2f} seconds")
    print(f"  Sample rate: {sample_rate:.1f} Hz")
    print(f"  Force range: {np.min(force_magnitude):.3f} - {np.max(force_magnitude):.3f} N")
    print(f"  Mean force: {np.mean(force_magnitude):.3f} ± {np.std(force_magnitude):.3f} N")
    print(f"  Torque range: {np.min(torque_magnitude):.3f} - {np.max(torque_magnitude):.3f} Nm")
    print(f"  Mean torque: {np.mean(torque_magnitude):.3f} ± {np.std(torque_magnitude):.3f} Nm")
```

## Troubleshooting

### Network Connectivity Issues
```python
def diagnose_network_issues(sensor_ip: str = "192.168.1.1"):
    """Comprehensive network diagnostics for ATI Delta sensor."""
    
    import subprocess
    import platform
    
    print("ATI Delta Network Diagnostics")
    print("=" * 40)
    
    # 1. Ping test
    print("1. Testing network connectivity...")
    
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "4", sensor_ip]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Ping successful to {sensor_ip}")
        else:
            print(f"✗ Ping failed to {sensor_ip}")
            print("  Check network cable and IP configuration")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ Ping timeout to {sensor_ip}")
        return False
    
    # 2. Port connectivity test
    print("2. Testing UDP port connectivity...")
    
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.settimeout(2.0)
        test_socket.bind(('', 0))  # Bind to any available port
        
        # Send test packet
        test_packet = struct.pack('>HH', 0x1234, 0x0000)
        test_socket.sendto(test_packet, (sensor_ip, 49152))
        
        # Wait for response
        response, addr = test_socket.recvfrom(1024)
        
        if len(response) > 0:
            print(f"✓ UDP communication successful on port 49152")
        else:
            print(f"✗ No response from sensor on port 49152")
            
        test_socket.close()
        
    except socket.timeout:
        print(f"✗ UDP communication timeout")
        print("  Check firewall settings and sensor power")
        return False
    except Exception as e:
        print(f"✗ UDP communication error: {e}")
        return False
    
    # 3. Sensor response test
    print("3. Testing sensor data response...")
    
    try:
        sensor = ATIDeltaSensor(sensor_ip)
        if sensor.connect():
            force_data = sensor.read_force_single()
            
            if any(abs(f) > 0.001 for f in force_data):
                print(f"✓ Sensor data received: {[f'{f:.3f}' for f in force_data]}")
            else:
                print(f"⚠ Sensor connected but all readings are zero")
                print("  Check sensor power and calibration")
            
            sensor.disconnect()
        else:
            print(f"✗ Failed to establish sensor communication")
            return False
            
    except Exception as e:
        print(f"✗ Sensor communication error: {e}")
        return False
    
    print("\n✓ All diagnostics passed")
    return True
```

### Data Quality Assessment
```python
def assess_data_quality(sensor: ATIDeltaSensor, duration: float = 30.0):
    """Assess sensor data quality and identify issues."""
    
    print(f"Assessing data quality for {duration} seconds...")
    
    # Collect baseline data
    baseline_samples = []
    for i in range(100):
        force_data = sensor.read_force_single()
        baseline_samples.append(force_data)
        time.sleep(0.01)
    
    # Calculate baseline statistics
    baseline_mean = [sum(sample[i] for sample in baseline_samples) / len(baseline_samples) 
                     for i in range(6)]
    baseline_std = [math.sqrt(sum((sample[i] - baseline_mean[i])**2 
                                 for sample in baseline_samples) / len(baseline_samples))
                    for i in range(6)]
    
    print("Baseline noise levels:")
    labels = ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']
    units = ['N', 'N', 'N', 'Nm', 'Nm', 'Nm']
    
    for i in range(6):
        print(f"  {labels[i]}: {baseline_mean[i]:.4f} ± {baseline_std[i]:.4f} {units[i]}")
    
    # Quality assessment criteria
    max_noise_force = 0.1  # N
    max_noise_torque = 0.01  # Nm
    
    quality_issues = []
    
    # Check noise levels
    if max(baseline_std[:3]) > max_noise_force:
        quality_issues.append(f"High force noise: {max(baseline_std[:3]):.4f} N")
    
    if max(baseline_std[3:]) > max_noise_torque:
        quality_issues.append(f"High torque noise: {max(baseline_std[3:]):.4f} Nm")
    
    # Check for drift
    print("\nChecking for drift...")
    
    drift_samples = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        force_data = sensor.read_force_single()
        drift_samples.append((time.time() - start_time, force_data))
        time.sleep(0.1)
    
    # Calculate drift rates
    timestamps = [sample[0] for sample in drift_samples]
    
    for i in range(6):
        values = [sample[1][i] for sample in drift_samples]
        
        # Linear regression for drift calculation
        n = len(timestamps)
        sum_t = sum(timestamps)
        sum_v = sum(values)
        sum_tv = sum(t * v for t, v in zip(timestamps, values))
        sum_t2 = sum(t * t for t in timestamps)
        
        # Drift rate (slope)
        drift_rate = (n * sum_tv - sum_t * sum_v) / (n * sum_t2 - sum_t * sum_t)
        
        # Check drift threshold
        max_drift_force = 0.01  # N/s
        max_drift_torque = 0.001  # Nm/s
        
        if i < 3 and abs(drift_rate) > max_drift_force:
            quality_issues.append(f"{labels[i]} drift: {drift_rate:.4f} N/s")
        elif i >= 3 and abs(drift_rate) > max_drift_torque:
            quality_issues.append(f"{labels[i]} drift: {drift_rate:.4f} Nm/s")
    
    # Report results
    if quality_issues:
        print("\nData Quality Issues Detected:")
        for issue in quality_issues:
            print(f"  ⚠ {issue}")
        
        print("\nRecommended Actions:")
        print("  - Check sensor mounting for vibration")
        print("  - Verify temperature stability")
        print("  - Consider re-calibration")
        print("  - Check for electromagnetic interference")
    else:
        print("\n✓ Data quality assessment passed")
    
    return len(quality_issues) == 0
```

## Maintenance and Calibration

### Regular Maintenance Schedule
- **Daily**: Visual inspection of sensor and cables
- **Weekly**: Verification of mounting security and alignment
- **Monthly**: Bias calibration and accuracy check with test weights
- **Quarterly**: Full calibration verification and documentation update
- **Annually**: Professional calibration service if required

### Calibration Verification
```python
def calibration_verification():
    """Verify sensor calibration using multiple test weights."""
    
    sensor = ATIDeltaSensor("192.168.1.1")
    sensor.connect()
    
    # Test weights (kg)
    test_weights = [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
    expected_forces = [w * 9.81 for w in test_weights]  # Convert to Newtons
    
    print("Calibration Verification Procedure")
    print("=" * 35)
    
    measured_forces = []
    
    for i, (weight, expected) in enumerate(zip(test_weights, expected_forces)):
        if weight == 0.0:
            print(f"Step {i+1}: Remove all weights, press Enter...")
        else:
            print(f"Step {i+1}: Place {weight}kg weight, press Enter...")
        
        input()
        
        # Take measurements
        readings = []
        for j in range(20):
            force_data = sensor.read_force_single()
            readings.append(abs(force_data[2]))  # Z-axis force
            time.sleep(0.05)
        
        measured = sum(readings) / len(readings)
        measured_forces.append(measured)
        
        error = abs(measured - expected)
        error_percent = (error / max(expected, 0.1)) * 100
        
        print(f"  Expected: {expected:.3f} N")
        print(f"  Measured: {measured:.3f} N")
        print(f"  Error: {error:.3f} N ({error_percent:.2f}%)")
        print()
    
    # Calculate linearity
    # Linear regression
    n = len(expected_forces)
    sum_x = sum(expected_forces)
    sum_y = sum(measured_forces)
    sum_xy = sum(x * y for x, y in zip(expected_forces, measured_forces))
    sum_x2 = sum(x * x for x in expected_forces)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    # Calculate R-squared
    y_mean = sum_y / n
    ss_tot = sum((y - y_mean)**2 for y in measured_forces)
    ss_res = sum((measured_forces[i] - (slope * expected_forces[i] + intercept))**2 
                 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot)
    
    print("Calibration Analysis:")
    print(f"  Slope: {slope:.6f}")
    print(f"  Intercept: {intercept:.6f} N")
    print(f"  R-squared: {r_squared:.6f}")
    print(f"  Linearity: {'PASS' if r_squared > 0.999 else 'FAIL'}")
    
    sensor.disconnect()
    
    return r_squared > 0.999
```

This comprehensive documentation provides everything needed to successfully integrate and operate ATI Delta IP60 force/torque sensors with Mecademic Meca500 robots for high-precision force sensing applications.