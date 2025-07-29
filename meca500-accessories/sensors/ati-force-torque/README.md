# ATI Force/Torque Sensor Integration

Integration system for connecting ATI Force/Torque sensors with Mecademic Meca500 robots using Python. Enables advanced force control applications including polishing, grinding, assembly, and force-guided trajectory teaching.

This repository provides complete Python implementations for:
- **NetFT Sensor Class**: UDP communication interface for ATI sensors
- **Force Control Applications**: Velocity-based movement with force feedback
- **Force-Guided Operations**: Manual robot guidance through force input
- **Trajectory Teaching**: Record and replay force-guided movements

## System Requirements

### Hardware Requirements
- **Robot**: Meca500-R3 or R4 with firmware 8.1.5+
- **Sensor**: ATI Mini40 Net F/T sensor or compatible ATI force/torque sensor
- **Connectivity**: M12-M12 D coded RJ45 cable
- **Power**: Net F/T sensor power supply
- **Computer**: Windows/Linux PC with network connectivity

### Software Requirements
- **Python**: 3.7 or higher
- **Dependencies**: 
  - PyQt5 (for GUI applications)
  - pyqtgraph (for real-time data visualization)
  - mecademicpy (Mecademic Python API)
  - socket (standard library)
  - struct (standard library)

## Communication Protocol

### UDP Interface
ATI Force/Torque sensors use UDP communication for real-time data streaming:
- **Protocol**: UDP over Ethernet
- **Default Port**: 49152
- **Data Rate**: Up to 7 kHz
- **Packet Format**: Binary force/torque values with timestamp

### NetFT Interface
The NetFT protocol provides:
- Real-time force/torque streaming
- Sensor configuration and calibration
- Bias removal and data filtering
- Multi-sensor support

## Velocity Control Mode

With firmware 8.1.5+, the Meca500 supports Velocity Control mode which enables:
- **Dynamic Path Planning**: Real-time trajectory modification
- **Non-buffered Commands**: Immediate response to force feedback
- **Complex Applications**: Force control and online path correction
- **Safety Features**: Automatic handling of joint limits and singularities

### Key Advantages
- Commands are not buffered like position control
- Controller doesn't enter error state on limit violations
- Enables reactive force control applications
- Supports real-time trajectory modification

## Application Examples

### 1. Force-Controlled Robot Move
Move robot towards surface until target force is reached:

```python
from netft_sensor import NetFTSensor
from mecademicpy import Robot

# Initialize sensor and robot
sensor = NetFTSensor('192.168.1.100')
robot = Robot()

# Move towards surface with force control
target_force = 10.0  # Newtons
velocity = [0, 0, -5, 0, 0, 0]  # Move down at 5 mm/s

while True:
    force_data = sensor.get_force()
    if abs(force_data[2]) >= target_force:  # Z-axis force
        robot.MoveVelTrf([0, 0, 0, 0, 0, 0])  # Stop movement
        break
    robot.MoveVelTrf(velocity)
```

### 2. Force-Guided Robot Jog
Map force sensor readings to robot movement for manual guidance:

```python
def force_guided_jog(sensor, robot, force_threshold=5.0):
    """Enable force-guided robot jogging"""
    while True:
        force_data = sensor.get_force()
        
        # Normalize force readings to velocity commands
        velocity = normalize_force_to_velocity(force_data, force_threshold)
        
        # Apply velocity command
        robot.MoveVelTrf(velocity)
        
        # Check for exit condition
        if exit_requested():
            robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
            break
```

### 3. Force-Guided Trajectory Teaching
Record robot poses during force-guided movement:

```python
def teach_trajectory(sensor, robot, filename):
    """Record trajectory during force-guided teaching"""
    trajectory = []
    
    while recording:
        force_data = sensor.get_force()
        pose = robot.GetPose()
        
        # Record pose with timestamp
        trajectory.append({
            'timestamp': time.time(),
            'pose': pose,
            'force': force_data
        })
        
        # Apply force-guided movement
        velocity = calculate_velocity_from_force(force_data)
        robot.MoveVelTrf(velocity)
    
    # Save trajectory to file
    save_trajectory(trajectory, filename)
```

### 4. Force-Based Testing/Inspection
Use force feedback for pass/fail validation:

```python
def force_test_sequence(sensor, robot, test_points):
    """Execute test sequence with force validation"""
    results = []
    
    for point in test_points:
        # Move to test position
        robot.MovePose(point['position'])
        
        # Apply test force
        apply_test_force(robot, point['test_force'])
        
        # Measure response
        measured_force = sensor.get_force()
        
        # Validate against expected range
        result = validate_force_range(measured_force, point['expected_range'])
        results.append(result)
    
    return results
```

## Implementation Files

### Core Components
- **File**: `python/netft_sensor.py`
- **Features**: NetFT UDP communication, sensor initialization, data streaming
- **Documentation**: Complete API reference with examples

### Application Examples
- **File**: `python/force_control_examples.py`
- **Features**: Force-controlled movement, polishing applications
- **Documentation**: Step-by-step implementation guide

- **File**: `python/force_guided_jog.py`
- **Features**: Manual robot guidance through force input
- **Documentation**: PyQt5 GUI implementation with threading

- **File**: `python/trajectory_teaching.py`
- **Features**: Record and replay force-guided trajectories
- **Documentation**: Trajectory file format and playback methods

## Quick Start

### Basic Sensor Connection
```python
from netft_sensor import NetFTSensor

# Initialize sensor connection
sensor = NetFTSensor('192.168.1.100')  # Sensor IP address

# Start data streaming
sensor.start_streaming()

# Read force/torque data
force_data = sensor.get_force()
print(f"Forces: Fx={force_data[0]:.2f}, Fy={force_data[1]:.2f}, Fz={force_data[2]:.2f}")
print(f"Torques: Tx={force_data[3]:.2f}, Ty={force_data[4]:.2f}, Tz={force_data[5]:.2f}")

# Clean up
sensor.stop_streaming()
```

### Force Control with Meca500
```python
from netft_sensor import NetFTSensor
from mecademicpy import Robot

# Initialize components
sensor = NetFTSensor('192.168.1.100')
robot = Robot()
robot.Connect('192.168.0.100')

# Enable velocity control mode
robot.SetVelTimeout(0.05)  # 50ms timeout for velocity commands

# Implement basic force control
target_force = 10.0
while True:
    force_data = sensor.get_force()
    current_force = abs(force_data[2])  # Z-axis force
    
    if current_force < target_force:
        # Move towards surface
        robot.MoveVelTrf([0, 0, -2, 0, 0, 0])  # 2 mm/s downward
    else:
        # Target force reached
        robot.MoveVelTrf([0, 0, 0, 0, 0, 0])  # Stop
        break

# Disconnect
robot.Disconnect()
```

## Network Configuration

### Sensor Network Settings
| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| **IP Address** | 192.168.1.100 | Sensor IP (configurable) |
| **Port** | 49152 | UDP data streaming port |
| **Data Rate** | 1000 Hz | Sampling frequency |
| **Timeout** | 1000ms | UDP socket timeout |

### Robot Network Settings
| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| **IP Address** | 192.168.0.100 | Robot controller IP |
| **API Port** | 10000 | Mecademic API port |
| **Velocity Timeout** | 50ms | Velocity command timeout |

## Setup Instructions

### 1. Hardware Setup
1. **Mount Sensor**: Install ATI sensor on robot flange or workpiece
2. **Connect Power**: Power the Net F/T sensor using provided supply
3. **Network Connection**: Connect sensor to network via Ethernet
4. **Cable Management**: Use appropriate strain relief for sensor cables

### 2. Software Configuration
1. **Install Dependencies**:
   ```bash
   pip install PyQt5 pyqtgraph mecademicpy
   ```

2. **Configure Network**: Set sensor and robot IP addresses
3. **Test Connection**: Verify sensor communication using test scripts
4. **Calibrate Sensor**: Run bias removal and calibration procedures

### 3. Application Development
1. **Start with Examples**: Use provided example scripts as templates
2. **Customize Parameters**: Adjust force thresholds and velocity limits
3. **Add Safety Checks**: Implement appropriate safety monitoring
4. **Test Thoroughly**: Validate force control behavior in safe environment

## Sensor Specifications

### ATI Mini40 Specifications
| Parameter | Value | Unit |
|-----------|-------|------|
| **Force Range** | ±40 | N |
| **Torque Range** | ±2 | Nm |
| **Resolution** | 1/80 | N, Nm |
| **Sampling Rate** | Up to 7000 | Hz |
| **Communication** | Ethernet | UDP/TCP |
| **Power** | 8-36 | VDC |

### Environmental Ratings
- **Operating Temperature**: -25°C to +85°C
- **Protection Rating**: IP60 (standard), IP65/IP68 (optional)
- **Shock Rating**: 100g for 11ms
- **EMI/EMC**: CE compliant

## Safety Considerations

### Force Limits
- **Maximum Force**: Do not exceed sensor rated capacity
- **Safety Factors**: Use appropriate safety margins (typically 2:1)
- **Overload Protection**: Implement software limits below hardware limits

### Velocity Control Safety
- **Emergency Stop**: Always implement accessible emergency stop
- **Workspace Limits**: Define and enforce safe workspace boundaries
- **Collision Detection**: Monitor for unexpected force increases
- **Timeout Handling**: Implement proper timeout for velocity commands

### Network Security
- **Isolated Network**: Use dedicated network for robot/sensor communication
- **Access Control**: Limit network access to authorized devices only
- **Monitoring**: Log all network communications for troubleshooting

## Troubleshooting

### Common Issues
1. **No Sensor Data**: Check network connectivity and IP configuration
2. **High Latency**: Verify network bandwidth and reduce data rate if needed
3. **Force Drift**: Perform sensor bias removal and recalibration
4. **Robot Stops**: Check velocity timeout settings and command frequency

### Diagnostic Tools
- **Network Ping**: Test basic connectivity to sensor
- **ATI NetFT Utility**: Official ATI software for sensor testing
- **Force Data Viewer**: Real-time force data visualization
- **Robot Log Files**: Check Meca500 logs for error messages

## Advanced Features

### Multi-Sensor Support
- Connect multiple ATI sensors for complex applications
- Synchronized data acquisition from multiple sensors
- Sensor fusion for enhanced force control

### Data Logging
- Real-time data logging to CSV files
- Synchronized force and position data
- Post-processing and analysis tools

### Custom Applications
- Template framework for developing custom force control applications
- Integration with existing automation systems
- Support for PLC and HMI interfaces

## Support and Resources

### Documentation
- [ATI NetFT Manual](https://www.ati-ia.com/library/documents/netft.pdf)
- [Mecademic Python API Documentation](https://mecademic.github.io/mecademicpy/)
- [Force Control Application Notes](https://support.mecademic.com)

### Example Files
All example files are provided as-is for reference and development:
- TouchScreenTestV2.zip
- PolishingV2.py
- Force_ControlV2.zip
- NetFT.py

### Disclaimer
These examples are provided as-is and serve as starting points for development. Mecademic and partners are not liable for any errors or unintended behavior. Users are responsible for implementing appropriate safety measures and validation procedures.