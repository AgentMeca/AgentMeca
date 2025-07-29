# ATI Force/Torque Sensor Python Implementation

Python modules for integrating ATI Force/Torque sensors with Mecademic Meca500 robots. Provides complete NetFT sensor interface and practical force control applications.

## Module Overview

### Core Components

#### netft_sensor.py
**NetFTSensor Class** - Complete UDP interface for ATI sensors
- Real-time force/torque data streaming
- Sensor configuration and calibration
- Bias removal and data filtering
- Thread-safe data access
- Context manager support

**Key Features:**
- UDP communication with configurable sample rates (1-7000 Hz)
- Automatic bias calculation and correction
- Real-time data streaming in separate thread
- Safety monitoring and error handling
- Support for multiple sensor models

#### force_control_examples.py
**Force Control Applications** - Practical implementation examples
- Surface approach with force feedback
- Constant force polishing/grinding
- Force-guided insertion operations
- Compliant contact control

**Application Classes:**
- `ForceController` - Base class with safety monitoring
- `SurfaceApproach` - Automated surface detection
- `ConstantForceControl` - PID-based force maintenance
- `ForceGuidedInsertion` - Compliant assembly operations

## Quick Start Guide

### 1. Basic Sensor Connection
```python
from netft_sensor import NetFTSensor

# Connect to sensor
sensor = NetFTSensor('192.168.1.100')
sensor.connect()
sensor.start_streaming(1000)  # 1 kHz sample rate

# Set bias (zero reference)
sensor.set_bias()

# Read force/torque data
force_data = sensor.get_force()
print(f"Forces: {force_data[:3]}")    # [Fx, Fy, Fz]
print(f"Torques: {force_data[3:]}")   # [Tx, Ty, Tz]

# Cleanup
sensor.disconnect()
```

### 2. Force Control with Robot
```python
from force_control_examples import SurfaceApproach

# Initialize force-controlled approach
approach = SurfaceApproach('192.168.0.100', '192.168.1.100')
approach.connect()

# Approach surface until 5N contact force
success = approach.approach_surface_z(target_force=5.0, 
                                     approach_velocity=2.0)

if success:
    print("Surface contact achieved")

approach.disconnect()
```

### 3. Constant Force Operations
```python
from force_control_examples import ConstantForceControl

# Initialize constant force controller
polisher = ConstantForceControl('192.168.0.100', '192.168.1.100')
polisher.connect()

# Define polishing trajectory
path = [[0, 0], [10, 0], [20, 0], [30, 0]]

# Execute polishing with 8N force
success = polisher.constant_force_polishing(target_force=8.0,
                                           polishing_trajectory=path)

polisher.disconnect()
```

## API Reference

### NetFTSensor Class

#### Constructor
```python
NetFTSensor(sensor_ip, sensor_port=49152, timeout=1.0)
```

#### Connection Methods
```python
connect() -> bool                    # Establish sensor connection
disconnect()                         # Close connection
start_streaming(sample_rate=1000)    # Start real-time data streaming
stop_streaming()                     # Stop data streaming
```

#### Data Access Methods
```python
get_force() -> List[float]           # Get [Fx, Fy, Fz, Tx, Ty, Tz]
get_force_xyz() -> Tuple             # Get (Fx, Fy, Fz) only
get_torque_xyz() -> Tuple            # Get (Tx, Ty, Tz) only
```

#### Calibration Methods
```python
set_bias(samples=100) -> bool        # Set bias using current readings
clear_bias()                         # Reset bias to zero
```

#### Utility Methods
```python
get_sensor_info() -> dict            # Get sensor status and configuration
```

### ForceController Classes

#### Base ForceController
```python
ForceController(robot_ip, sensor_ip)
connect() -> bool                    # Connect to robot and sensor
disconnect()                         # Disconnect all components
check_safety_limits() -> bool        # Verify forces within safe limits
```

#### SurfaceApproach
```python
approach_surface_z(target_force=5.0, approach_velocity=2.0, max_distance=50.0) -> bool
```
- **target_force**: Contact force threshold (N)
- **approach_velocity**: Approach speed (mm/s)  
- **max_distance**: Maximum travel distance (mm)

#### ConstantForceControl
```python
constant_force_polishing(target_force=10.0, polishing_trajectory=None, lateral_velocity=5.0) -> bool
```
- **target_force**: Maintained contact force (N)
- **polishing_trajectory**: List of [x, y] positions
- **lateral_velocity**: Lateral movement speed (mm/s)

#### ForceGuidedInsertion
```python
compliant_insertion(insertion_depth=20.0, max_insertion_force=20.0, max_lateral_force=5.0) -> bool
```
- **insertion_depth**: Target insertion depth (mm)
- **max_insertion_force**: Force limit for insertion direction (N)
- **max_lateral_force**: Force limit for lateral directions (N)

## Configuration Parameters

### Sensor Configuration
```python
# Sample rates (Hz)
SUPPORTED_RATES = [1, 10, 100, 500, 1000, 2000, 7000]

# Default network settings
DEFAULT_PORT = 49152
DEFAULT_TIMEOUT = 1.0

# Data format
FORCE_CHANNELS = ['Fx', 'Fy', 'Fz']      # Forces in Newtons
TORQUE_CHANNELS = ['Tx', 'Ty', 'Tz']     # Torques in Newton-meters
```

### Force Control Parameters
```python
# Safety limits
MAX_FORCE = 50.0        # Maximum allowable force (N)
MAX_TORQUE = 5.0        # Maximum allowable torque (Nm)

# Control frequencies
CONTROL_FREQUENCY = 50  # Force control loop frequency (Hz)
VELOCITY_TIMEOUT = 0.05 # Robot velocity command timeout (s)

# PID tuning (adjust for your application)
KP_FORCE = 0.5         # Proportional gain
KI_FORCE = 0.01        # Integral gain
KD_FORCE = 0.05        # Derivative gain
```

## Installation Requirements

### Python Dependencies
```bash
pip install mecademicpy PyQt5 pyqtgraph
```

### System Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows 10/11, Ubuntu 18.04+
- **Network**: Ethernet connectivity to robot and sensor
- **Hardware**: ATI NetFT compatible sensor

### Network Configuration
1. **Sensor IP**: Configure static IP for ATI sensor
2. **Robot IP**: Configure Meca500 IP address  
3. **PC Network**: Ensure PC can communicate with both devices
4. **Firewall**: Allow UDP traffic on sensor port (49152)

## Application Examples

### Example 1: Surface Detection
```python
# Automated surface detection for unknown workpieces
from netft_sensor import NetFTSensor
from force_control_examples import SurfaceApproach

def detect_surface():
    approach = SurfaceApproach('192.168.0.100', '192.168.1.100')
    
    if approach.connect():
        # Slow, precise approach
        success = approach.approach_surface_z(
            target_force=2.0,      # Light contact
            approach_velocity=1.0, # Slow approach
            max_distance=30.0      # Search within 30mm
        )
        
        if success:
            print("Surface detected and contacted")
            # Continue with subsequent operations
        
        approach.disconnect()
```

### Example 2: Precision Polishing
```python
# Constant force polishing with complex trajectory
def precision_polishing():
    polisher = ConstantForceControl('192.168.0.100', '192.168.1.100')
    
    # Generate circular polishing pattern
    import math
    circle_points = []
    for angle in range(0, 360, 10):
        x = 20 * math.cos(math.radians(angle))
        y = 20 * math.sin(math.radians(angle))
        circle_points.append([x, y])
    
    if polisher.connect():
        success = polisher.constant_force_polishing(
            target_force=12.0,
            polishing_trajectory=circle_points,
            lateral_velocity=4.0
        )
        polisher.disconnect()
```

### Example 3: Compliant Assembly
```python
# Force-guided peg insertion with compliance
def peg_insertion():
    inserter = ForceGuidedInsertion('192.168.0.100', '192.168.1.100')
    
    if inserter.connect():
        # Multi-stage insertion
        stages = [
            {'depth': 5.0, 'force': 5.0},   # Initial contact
            {'depth': 10.0, 'force': 10.0}, # Partial insertion
            {'depth': 20.0, 'force': 15.0}  # Full insertion
        ]
        
        for stage in stages:
            success = inserter.compliant_insertion(
                insertion_depth=stage['depth'],
                max_insertion_force=stage['force'],
                max_lateral_force=3.0
            )
            
            if not success:
                print(f"Insertion failed at stage: {stage}")
                break
        
        inserter.disconnect()
```

## Troubleshooting

### Common Issues

#### Connection Problems
```python
# Test sensor connectivity
def test_sensor_connection(sensor_ip):
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        sock.sendto(b'\x12\x34\x00\x00\x00\x01', (sensor_ip, 49152))
        response, addr = sock.recvfrom(1024)
        print(f"Sensor responds: {len(response)} bytes")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
```

#### Force Data Issues
```python
# Validate force data
def validate_force_data(sensor):
    for i in range(10):
        force_data = sensor.get_force()
        force_magnitude = sum(f*f for f in force_data[:3])**0.5
        
        if force_magnitude > 100:  # Unrealistic force
            print(f"Warning: High force reading: {force_magnitude:.2f} N")
        
        time.sleep(0.1)
```

#### Robot Communication
```python
# Verify robot connection
def test_robot_connection(robot_ip):
    try:
        from mecademicpy import Robot
        robot = Robot()
        robot.Connect(robot_ip, enable_synchronous_mode=False)
        
        if robot.GetStatusRobot().connection_status:
            print("Robot connected successfully")
            robot.Disconnect()
            return True
        else:
            print("Robot connection failed")
            return False
    except Exception as e:
        print(f"Robot error: {e}")
        return False
```

### Performance Optimization

#### High-Frequency Control
```python
# Optimize for high-frequency force control
def optimize_performance(sensor, robot):
    # Use higher sample rate
    sensor.start_streaming(2000)  # 2 kHz
    
    # Reduce velocity timeout
    robot.SetVelTimeout(0.02)  # 20ms
    
    # Use dedicated control thread
    import threading
    
    def control_loop():
        while control_active:
            force_data = sensor.get_force()
            # Implement control logic
            time.sleep(0.01)  # 100 Hz control
    
    control_thread = threading.Thread(target=control_loop)
    control_thread.start()
```

### Safety Guidelines

#### Force Monitoring
```python
# Continuous safety monitoring
class SafetyMonitor:
    def __init__(self, sensor, max_force=30.0):
        self.sensor = sensor
        self.max_force = max_force
        self.monitoring = False
    
    def start_monitoring(self):
        self.monitoring = True
        threading.Thread(target=self._monitor_loop).start()
    
    def _monitor_loop(self):
        while self.monitoring:
            force_data = self.sensor.get_force()
            force_mag = sum(f*f for f in force_data[:3])**0.5
            
            if force_mag > self.max_force:
                print("EMERGENCY: Force limit exceeded!")
                # Trigger emergency stop
                
            time.sleep(0.01)
```

## Advanced Features

### Data Logging
```python
# Comprehensive data logging
import csv
import datetime

def log_force_data(sensor, filename=None):
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"force_data_{timestamp}.csv"
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz'])
        
        start_time = time.time()
        while time.time() - start_time < 60:  # Log for 60 seconds
            force_data = sensor.get_force()
            timestamp = time.time()
            writer.writerow([timestamp] + force_data)
            time.sleep(0.01)  # 100 Hz logging
```

### Custom Applications
```python
# Template for custom force control applications
class CustomForceApplication(ForceController):
    def __init__(self, robot_ip, sensor_ip):
        super().__init__(robot_ip, sensor_ip)
        # Add custom initialization
    
    def custom_operation(self, parameters):
        """Implement your custom force control operation."""
        if not self.connect():
            return False
        
        try:
            # Implement custom logic here
            # Use self.robot and self.sensor
            # Apply force control algorithms
            # Monitor safety limits
            
            return True
            
        except Exception as e:
            print(f"Custom operation error: {e}")
            return False
        finally:
            self.disconnect()
```

This Python implementation provides a comprehensive foundation for developing advanced force control applications with ATI sensors and Meca500 robots. All examples include proper error handling, safety monitoring, and performance optimization for production use.