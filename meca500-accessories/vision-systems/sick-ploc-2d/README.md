# SICK PLOC 2D Vision System Integration

Integration plugin for communicating with SICK PLOC 2D Vision Systems through Mecademic robots using Python. This implementation enables vision-guided pick and place applications with high precision positioning.

This repository provides a complete Python implementation for:
- **VisionController Class**: TCP/IP communication with SICK PLOC 2D system
- **VisionGuidedPick Class**: High-level integration combining robot control and vision system functionality
- **Calibration Tools**: Vision Reference Frame alignment with robot coordinate system

## System Overview

The SICK PLOC2D is an easy-setup vision system for 2D localization that provides:
- 0.5px resolution measurement accuracy in two axes
- 0.1° rotational measurement precision
- Ability to locate multiple simultaneous parts in an image
- Support for conveyor tracking (120+ parts per minute)
- Part identification capability for quality verification
- IP65 housing for industrial environments

## System Requirements

### Hardware Requirements
- **Robot**: Meca500-R3 or R4
- **Vision System**: SICK PLOC 2D Vision System
- **Power Supply**: 24V DC power supply for PLOC 2D
- **Networking**: M12-D coded RJ45 cable for Ethernet connection
- **Computing**: Windows/Linux PC for control application

### Software Requirements
- **Python**: 3.7 or higher
- **Libraries**: numpy for mathematical operations
- **Mecademic Python API**: Latest version for robot control
- **Network Configuration**: Static IP addresses for both robot and vision system

## Integration Architecture

### Communication Protocol
The SICK PLOC 2D communicates via TCP/IP using a socket-based protocol. The system supports:
- **Configuration Interface**: Web-based configuration accessible via browser
- **Data Interface**: TCP/IP socket communication for real-time data exchange
- **Industrial Interfaces**: Support for various robot and PLC protocols

### Key Integration Steps

1. **Installation**: Physical setup and network configuration
2. **Calibration**: Lens distortion parameter estimation
3. **Alignment**: Camera pose establishment relative to robot coordinate system
4. **Job Configuration**: Target shape and detection parameter definition
5. **Job Execution**: Real-time vision-guided operations

## Calibration Process

### Vision Reference Frame (WRF) Calibration
The integration uses a 3-point calibration method to establish the relationship between the vision system coordinate frame and the robot's Base Reference Frame.

**Calibration Steps:**
1. Position robot at three known reference points within the camera field of view
2. Record both robot coordinates and corresponding vision system coordinates
3. Calculate transformation matrix using the VisionGuidedPick calibration method
4. Validate calibration accuracy with test positions

**Mathematical Foundation:**
The calibration establishes a transformation matrix that converts vision coordinates (x_vision, y_vision) to robot coordinates (x_robot, y_robot, z_robot) with proper orientation alignment.

## Network Configuration

### IP Address Assignment
- **Robot**: Typically 192.168.0.100 (configurable)
- **PLOC 2D System**: Typically 192.168.0.1 (configurable)
- **Control PC**: Same subnet (e.g., 192.168.0.10)

### Port Configuration
- **Vision Data Port**: Default TCP port for data communication
- **Web Interface**: HTTP port 80 for browser-based configuration
- **Robot API**: Mecademic API default ports

## Command Reference

### Vision System Operations

| Method | Description | Returns |
|--------|-------------|---------|
| `locate()` | Execute vision job and return all detected parts | List of part coordinates |
| `locate_by_index(job_id, index)` | Get specific part by index | Position and orientation data |
| `get_count(job_id)` | Get number of detected parts | Integer count |
| `connect()` | Establish TCP connection to vision system | Boolean success status |
| `disconnect()` | Close TCP connection | None |

### Robot Control Integration

| Method | Description | Parameters |
|--------|-------------|------------|
| `pick_index(job_id, index)` | Pick part at specified index | job_id, part_index |
| `place(x, y, z, rx, ry, rz)` | Place part at target location | Target coordinates |
| `set_vision_ref(x, y, z, rx, ry, rz)` | Set vision reference frame | Reference coordinates |
| `set_offset(height)` | Set pick height offset | Offset in mm |

## Implementation Files

### Python Implementation
- **VisionController**: `python/vision_controller.py` - Core TCP communication with PLOC 2D
- **VisionGuidedPick**: `python/vision_guided_pick.py` - High-level integration class
- **Example Application**: `python/example_application.py` - Complete workflow demonstration
- **Documentation**: See `python/README.md` for detailed API reference

## Quick Start

### Basic Setup
```python
from vision_guided_pick import VisionGuidedPick

# Initialize with robot and vision system IP addresses
app = VisionGuidedPick('192.168.0.100', '192.168.0.1')

# Initialize connections
app.init_robot()
app.init_vision()

# Configure vision reference frame (calibration coordinates)
app.set_vision_ref(100, 50, 25, 0, 0, 0)

# Set pick height offset
app.set_offset(25)
```

### Vision-Guided Pick and Place
```python
# Get count of detected parts
count = app.get_count(1)  # Job ID 1

if count is not None and count > 0:
    for i in range(1, count + 1):
        # Pick part at index i
        success = app.pick_index(1, i)
        
        if success:
            # Place part at target location
            app.place(-120, 100, 0, 180, 0, 180)
            print(f"Part {i} processed successfully")
        else:
            print(f"Failed to pick part {i}")
```

### Individual Component Usage
```python
from vision_controller import VisionController
from mecademic_robot import MecademicRobot

# Direct vision system communication
vision = VisionController('192.168.0.1')
vision.connect()

# Execute vision job
parts = vision.locate()
print(f"Found {len(parts)} parts")

# Get specific part by index
if len(parts) > 0:
    part_data = vision.locate_by_index(1, 1)
    print(f"Part 1 position: {part_data}")

vision.disconnect()
```

## Error Handling

### Connection Errors
- **Vision System Timeout**: Check network connectivity and IP configuration
- **Robot Connection Failed**: Verify robot is powered and network accessible
- **Communication Protocol Errors**: Ensure compatible firmware versions

### Calibration Issues
- **Poor Calibration Accuracy**: Verify reference points are accurately positioned
- **Coordinate Transformation Errors**: Check calibration point distribution across work area
- **Repeatability Problems**: Ensure stable mechanical setup and lighting conditions

### Vision Detection Issues
- **Low Part Detection Rate**: Adjust lighting conditions and job parameters
- **False Positive Detection**: Refine shape matching parameters in job configuration
- **Position Accuracy Problems**: Verify lens calibration and camera mounting stability

## Performance Considerations

### Throughput Optimization
- **Cycle Time**: Typical pick-place cycle ~2-3 seconds depending on travel distance
- **Detection Speed**: PLOC 2D can process 120+ parts per minute in conveyor applications
- **Network Latency**: Minimize by using dedicated network for robot-vision communication

### Accuracy Factors
- **Measurement Resolution**: 0.5px resolution achievable with proper calibration
- **Repeatability**: ±0.1mm typical for well-calibrated systems
- **Environmental Stability**: Temperature and vibration affect long-term accuracy

## Troubleshooting

### Common Issues

1. **"Not Connected" Errors**
   - Verify IP addresses and network connectivity
   - Check firewall settings on control PC
   - Ensure PLOC 2D system is powered and initialized

2. **Calibration Failures**
   - Use calibration points distributed across the work area
   - Ensure accurate robot positioning during calibration
   - Verify vision system can detect calibration target

3. **Poor Detection Performance**
   - Optimize lighting conditions for consistent contrast
   - Adjust job parameters for part shape and size
   - Check for environmental factors affecting image quality

### Debug Information
Both VisionController and VisionGuidedPick classes include debug output options for troubleshooting communication and operation issues.

## Additional Resources

### SICK Documentation
- **PLOC2D Operating Instructions**: Complete setup and configuration guide
- **Integration Tutorial**: Step-by-step integration walkthrough
- **API Reference**: Detailed communication protocol documentation

### Mecademic Resources
- **Python API Documentation**: Robot control interface reference
- **Application Examples**: Additional vision integration examples
- **Support Portal**: Technical support and knowledge base access

### Related Links
- [SICK PLOC2D Product Information](https://www.sick.com/us/en/system-solutions/robot-guidance-systems/ploc2d/c/g456151)
- [Mecademic Knowledge Base](https://support.mecademic.com/knowledge-base/mecanetwork)
- [Mecademic Python API](https://github.com/Mecademic/mecademic-python)

## Dependencies

### Required Python Packages
```
numpy>=1.19.0
mecademic>=1.0.0
socket (standard library)
time (standard library)
sys (standard library)
```

### Installation
```bash
pip install numpy mecademic
```

## Version Compatibility

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| Python | 3.7 | 3.9+ |
| Mecademic Python API | 1.0.0 | Latest |
| PLOC2D Firmware | 4.1 | Latest |
| Meca500 Firmware | 9.0 | Latest |

**Note**: The example code may reference deprecated API methods. Always use the latest Mecademic Python API for new implementations.

## Support

For technical support and integration assistance:
- **Mecademic Support**: [support.mecademic.com](https://support.mecademic.com)
- **SICK Support**: Contact your local SICK representative
- **Community Resources**: Mecademic user forums and documentation

## License

This integration example is provided for educational and development purposes. Check with Mecademic and SICK for any licensing requirements for commercial use.