# Python SICK PLOC 2D Integration

Python modules for integrating SICK PLOC 2D Vision Systems with Mecademic robots. This implementation provides two main classes for vision-guided automation applications.

## Module Overview

- **VisionController**: Direct TCP/IP communication with SICK PLOC 2D system
- **VisionGuidedPick**: High-level integration combining vision and robot control
- **Example Application**: Complete workflow demonstration

## Features

- **TCP/IP Communication**: Direct socket connection to PLOC 2D system
- **Vision-Robot Calibration**: 3-point calibration method for coordinate transformation
- **Automated Pick and Place**: Complete workflow with error handling
- **Flexible Configuration**: Configurable offsets, speeds, and operational parameters
- **Debug Support**: Comprehensive logging for troubleshooting
- **Context Manager Support**: Automatic resource cleanup

## VisionController Class

### Overview
The `VisionController` class provides direct TCP/IP communication with the SICK PLOC 2D Vision System. It handles all low-level protocol communication and data parsing.

### Initialization
```python
from vision_controller import VisionController

# Initialize with IP address and optional parameters
vision = VisionController(
    ip_address="192.168.0.1",
    port=2005,              # Default TCP port
    timeout=5.0,            # Socket timeout in seconds
    debug=True              # Enable debug output
)
```

### Connection Management
```python
# Connect to vision system
if vision.connect():
    print("Connected successfully")
    
    # Your vision operations here
    
    # Disconnect when done
    vision.disconnect()

# Or use context manager for automatic cleanup
with VisionController("192.168.0.1", debug=True) as vision:
    # Operations here
    pass  # Automatic disconnect
```

### Core Methods

#### `connect() -> bool`
Establish TCP connection to PLOC 2D system.
```python
success = vision.connect()
if not success:
    print("Connection failed")
```

#### `disconnect() -> None`
Close TCP connection to PLOC 2D system.
```python
vision.disconnect()
```

#### `locate(job_id: int = 1) -> Optional[List[Dict[str, float]]]`
Execute vision job and return all detected parts.
```python
parts = vision.locate(job_id=1)
if parts:
    for i, part in enumerate(parts):
        print(f"Part {i+1}: x={part['x']:.2f}, y={part['y']:.2f}, rz={part['rz']:.2f}")
```

**Returns:** List of dictionaries with keys: `'x'`, `'y'`, `'z'`, `'rz'`

#### `locate_by_index(job_id: int, part_index: int) -> Optional[Dict[str, float]]`
Get specific part data by index.
```python
part = vision.locate_by_index(1, 1)  # Get first part from job 1
if part:
    print(f"Position: ({part['x']}, {part['y']}, {part['z']})")
    print(f"Rotation: {part['rz']} degrees")
```

#### `get_part_count(job_id: int) -> Optional[int]`
Get number of detected parts.
```python
count = vision.get_part_count(1)
if count is not None:
    print(f"Found {count} parts")
```

#### `get_system_status() -> Dict[str, Any]`
Get system status information.
```python
status = vision.get_system_status()
print(f"Connected: {status['connected']}")
print(f"System Ready: {status['system_ready']}")
```

#### `set_job_parameters(job_id: int, parameters: Dict[str, Any]) -> bool`
Configure vision job parameters.
```python
params = {
    'threshold': 128,
    'min_area': 100,
    'max_area': 10000
}
success = vision.set_job_parameters(1, params)
```

## VisionGuidedPick Class

### Overview
The `VisionGuidedPick` class provides high-level integration between SICK PLOC 2D vision system and Mecademic robot control for automated pick and place operations.

### Initialization
```python
from vision_guided_pick import VisionGuidedPick

# Initialize with robot and vision IP addresses
app = VisionGuidedPick(
    robot_ip="192.168.0.100",
    vision_ip="192.168.0.1",
    debug=True
)
```

### System Initialization
```python
# Initialize robot connection
if not app.init_robot():
    print("Robot initialization failed")
    exit(1)

# Initialize vision system
if not app.init_vision():
    print("Vision initialization failed")
    exit(1)
```

### Calibration Methods

#### `set_vision_ref(x, y, z, rx, ry, rz) -> None`
Set vision reference frame using single calibration point.
```python
# Set reference point coordinates (robot coordinates)
app.set_vision_ref(
    x=100.0,   # X coordinate (mm)
    y=50.0,    # Y coordinate (mm) 
    z=25.0,    # Z coordinate (mm)
    rx=0.0,    # X rotation (degrees)
    ry=0.0,    # Y rotation (degrees)
    rz=0.0     # Z rotation (degrees)
)
```

#### `calibrate_3_point(robot_points, vision_points) -> bool`
Perform 3-point calibration for accurate coordinate transformation.
```python
# Define calibration points
robot_points = [
    (100.0, 100.0, 25.0),  # Point 1: robot coordinates
    (200.0, 100.0, 25.0),  # Point 2: robot coordinates
    (150.0, 200.0, 25.0)   # Point 3: robot coordinates
]

vision_points = [
    (320, 240),   # Point 1: vision coordinates
    (420, 240),   # Point 2: vision coordinates  
    (370, 340)    # Point 3: vision coordinates
]

success = app.calibrate_3_point(robot_points, vision_points)
if success:
    print("Calibration completed successfully")
```

### Configuration Methods

#### `set_offset(pick_offset, place_offset=None) -> None`
Set Z-axis offsets for pick and place operations.
```python
app.set_offset(
    pick_offset=5.0,   # Pick 5mm above part
    place_offset=10.0  # Place 10mm above target (optional)
)
```

#### `set_speed(speed) -> None`
Set robot movement speed (1-100%).
```python
app.set_speed(25.0)  # 25% speed
```

### Operation Methods

#### `get_count(job_id: int) -> Optional[int]`
Get number of parts detected by vision system.
```python
count = app.get_count(1)
if count and count > 0:
    print(f"Ready to process {count} parts")
```

#### `pick_index(job_id: int, part_index: int) -> bool`
Pick part at specified index using vision guidance.
```python
success = app.pick_index(1, 1)  # Pick first part from job 1
if success:
    print("Part picked successfully")
else:
    print("Pick operation failed")
```

#### `place(x, y, z, rx, ry, rz) -> bool`
Place part at specified coordinates.
```python
success = app.place(
    x=-120.0,   # Target X coordinate
    y=100.0,    # Target Y coordinate  
    z=0.0,      # Target Z coordinate
    rx=180.0,   # Target X rotation
    ry=0.0,     # Target Y rotation
    rz=180.0    # Target Z rotation
)
```

#### `shutdown() -> None`
Safely shutdown robot and vision systems.
```python
app.shutdown()  # Manual shutdown

# Or use context manager for automatic shutdown
with VisionGuidedPick(robot_ip, vision_ip) as app:
    # Operations here
    pass  # Automatic shutdown
```

## Complete Workflow Example

### Basic Pick and Place
```python
from vision_guided_pick import VisionGuidedPick

# System configuration
robot_ip = "192.168.0.100"
vision_ip = "192.168.0.1"

# Initialize system
app = VisionGuidedPick(robot_ip, vision_ip, debug=True)

try:
    # Initialize components
    if not app.init_robot():
        raise Exception("Robot initialization failed")
    
    if not app.init_vision():
        raise Exception("Vision initialization failed")
    
    # Configure system
    app.set_vision_ref(100, 50, 25, 0, 0, 0)  # Set calibration
    app.set_offset(5.0)                        # Set pick offset
    app.set_speed(25.0)                        # Set movement speed
    
    # Execute workflow
    job_id = 1
    count = app.get_count(job_id)
    
    if count and count > 0:
        print(f"Processing {count} parts")
        
        for i in range(1, count + 1):
            print(f"Processing part {i}/{count}")
            
            # Pick part
            if app.pick_index(job_id, i):
                # Place part
                if app.place(-120, 100, 0, 180, 0, 180):
                    print(f"Part {i} completed successfully")
                else:
                    print(f"Failed to place part {i}")
            else:
                print(f"Failed to pick part {i}")
    else:
        print("No parts detected")

finally:
    app.shutdown()
```

### Advanced Workflow with 3-Point Calibration
```python
from vision_guided_pick import VisionGuidedPick
from vision_controller import VisionController

# Initialize systems
app = VisionGuidedPick("192.168.0.100", "192.168.0.1", debug=True)

try:
    # Initialize components
    app.init_robot()
    app.init_vision()
    
    # Perform 3-point calibration
    robot_calibration_points = [
        (100.0, 100.0, 25.0),
        (200.0, 100.0, 25.0), 
        (150.0, 200.0, 25.0)
    ]
    
    # Move robot to each calibration point and record vision coordinates
    vision_calibration_points = []
    
    for i, (x, y, z) in enumerate(robot_calibration_points):
        # Move robot to calibration point
        app.robot.MoveCartPoint(x, y, z, 0, 0, 0)
        app.robot.WaitMovementCompletion()
        
        # Get vision coordinates at this position
        input(f"Position robot at calibration point {i+1} and press Enter...")
        
        # Record vision coordinates (this would typically be automated)
        vision_x = float(input(f"Enter vision X coordinate for point {i+1}: "))
        vision_y = float(input(f"Enter vision Y coordinate for point {i+1}: "))
        vision_calibration_points.append((vision_x, vision_y))
    
    # Perform calibration
    success = app.calibrate_3_point(robot_calibration_points, vision_calibration_points)
    
    if success:
        print("Calibration successful - ready for production")
        
        # Continue with normal operation
        app.set_offset(5.0)
        app.set_speed(25.0)
        
        # Production loop
        while True:
            count = app.get_count(1)
            if count and count > 0:
                for i in range(1, count + 1):
                    if app.pick_index(1, i):
                        app.place(-120, 100, 0, 180, 0, 180)
            else:
                time.sleep(1.0)  # Wait for new parts
    
    else:
        print("Calibration failed")

finally:
    app.shutdown()
```

## Error Handling

### Connection Errors
```python
try:
    vision = VisionController("192.168.0.1", debug=True)
    if not vision.connect():
        print("Failed to connect to vision system")
        # Check network connectivity, IP addresses, firewall settings
        
except Exception as e:
    print(f"Vision system error: {e}")
```

### Robot Errors
```python
try:
    app = VisionGuidedPick("192.168.0.100", "192.168.0.1")
    if not app.init_robot():
        print("Robot initialization failed")
        # Check robot power, network, firmware version
        
except Exception as e:
    print(f"Robot error: {e}")
```

### Operation Errors
```python
# Pick operation with error handling
success = app.pick_index(1, 1)
if not success:
    # Check part detection, calibration accuracy, gripper status
    print("Pick failed - checking system status...")
    
    status = app.vision.get_system_status()
    if not status['connected']:
        print("Vision system disconnected")
        app.init_vision()
    
    # Retry operation
    success = app.pick_index(1, 1)
```

## Performance Optimization

### Cycle Time Optimization
```python
# Optimize for speed
app.set_speed(50.0)          # Increase speed
app.set_offset(3.0)          # Reduce pick offset

# Batch operations
count = app.get_count(1)
if count > 0:
    # Process all parts without individual status checks
    for i in range(1, count + 1):
        app.pick_index(1, i)
        app.place(-120, 100, 0, 180, 0, 180)
```

### Communication Optimization
```python
# Minimize vision system communication
vision = VisionController("192.168.0.1", timeout=2.0)  # Reduce timeout

# Cache part data
parts = vision.locate(1)  # Get all parts at once
for i, part in enumerate(parts):
    # Use cached data instead of individual queries
    robot_coords = app._transform_vision_to_robot(part['x'], part['y'])
    # Process part...
```

## Troubleshooting

### Common Issues

#### "Not Connected" Errors
```python
# Check network connectivity
import socket

def test_connection(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

if not test_connection("192.168.0.1", 2005):
    print("Cannot reach vision system - check network configuration")
```

#### Calibration Issues
```python
# Verify calibration accuracy
def test_calibration(app):
    # Move to known position
    test_x, test_y, test_z = 150.0, 150.0, 25.0
    app.robot.MoveCartPoint(test_x, test_y, test_z, 0, 0, 0)
    app.robot.WaitMovementCompletion()
    
    # Get vision coordinates
    parts = app.vision.locate(1)
    if parts:
        vision_coords = (parts[0]['x'], parts[0]['y'])
        robot_coords = app._transform_vision_to_robot(*vision_coords)
        
        error_x = abs(robot_coords[0] - test_x)
        error_y = abs(robot_coords[1] - test_y)
        
        print(f"Calibration error: X={error_x:.2f}mm, Y={error_y:.2f}mm")
        
        if error_x > 2.0 or error_y > 2.0:
            print("Poor calibration - recalibration recommended")
```

#### Performance Issues
```python
# Monitor cycle times
import time

start_time = time.time()

# Your pick and place operation
app.pick_index(1, 1)
app.place(-120, 100, 0, 180, 0, 180)

cycle_time = time.time() - start_time
print(f"Cycle time: {cycle_time:.2f} seconds")

if cycle_time > 5.0:
    print("Slow cycle time - consider optimization")
```

## Dependencies

### Required Packages
```bash
pip install numpy mecademic
```

### Standard Library Modules
- `socket` - TCP/IP communication
- `time` - Timing and delays  
- `sys` - System interface
- `typing` - Type hints

### Optional Dependencies
- `matplotlib` - For calibration visualization
- `opencv-python` - For advanced image processing

## Version Compatibility

| Component | Minimum Version | Tested Version |
|-----------|----------------|----------------|
| Python | 3.7 | 3.9+ |
| numpy | 1.19.0 | Latest |
| mecademic | 1.0.0 | Latest |
| SICK PLOC2D | 4.1 | 4.1+ |

## Best Practices

### System Setup
1. Use static IP addresses for all components
2. Ensure stable network connectivity
3. Perform calibration in production lighting conditions
4. Validate calibration accuracy before production

### Error Handling
1. Always check return values for critical operations
2. Implement retry logic for network operations
3. Monitor system status during operation
4. Log errors for troubleshooting

### Performance
1. Minimize network communication overhead
2. Use appropriate timeouts for your application
3. Cache frequently accessed data
4. Optimize robot speeds for your accuracy requirements

### Safety
1. Always test new calibrations with known objects
2. Implement emergency stop procedures
3. Monitor robot workspace for obstacles
4. Use appropriate safety interlocks

## Support and Resources

### Documentation
- [SICK PLOC2D Manual](https://www.sick.com/us/en/system-solutions/robot-guidance-systems/ploc2d/c/g456151)
- [Mecademic Python API](https://github.com/Mecademic/mecademic-python)
- [Integration Tutorial](https://support.mecademic.com/knowledge-base/meca500-sick-ploc-2d-vision-system-integration-using-python)

### Support
- **Mecademic Support**: support.mecademic.com
- **SICK Support**: Contact local SICK representative
- **Community Forums**: Mecademic user community