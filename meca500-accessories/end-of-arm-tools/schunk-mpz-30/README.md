# Schunk MPZ-30 Pneumatic Gripper Integration

Integration guide for the Schunk MPZ-30 three-finger centric pneumatic gripper with Mecademic Meca500 robots.

## Overview

The Schunk MPZ-30 is a compact, three-finger centric double-acting pneumatic gripper designed for high-precision gripping applications. This integration provides complete setup instructions, hardware requirements, and sample code for seamless operation with the Meca500 robot.

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Gripper Type** | 3-finger centric double-acting pneumatic |
| **Stroke per Jaw** | 3 mm |
| **Closing Force** | 55 N |
| **Opening Force** | 65 N |
| **Weight** | 0.1 kg |
| **Max Operating Pressure** | 8 bar |
| **Repeat Accuracy** | 0.01 mm |

## Required Components

### Hardware
- Meca500 Robot (firmware 8.1.6 or above)
- MPM500 Pneumatic Module
- Schunk MPZ-30 Pneumatic Gripper
- Custom mounting bracket (see STL files)
- Custom gripper fingers (see STL files)
- M3x0.5 screws (for finger attachment and bracket mounting)
- M4x0.7 screws (for gripper-to-bracket mounting)
- M5 threaded barb fittings (included with MPM500)
- M3 threaded barb fittings (purchased separately)
- 1/16 inch ID or 4mm OD pneumatic cables

### Software
- Mecademic Robot Programming Interface
- 3D printer for custom brackets and fingers (optional if fabricated elsewhere)

## Prerequisites

Before beginning the integration, ensure you have:
1. Reviewed the [Meca500 User Manual](https://www.mecademic.com/resources/documentation)
2. Reviewed the [MPM500 User Manual](https://www.mecademic.com/resources/documentation)
3. Verified MPM500 installation and proper operation
4. Downloaded and prepared the custom mounting hardware STL files
5. Confirmed adequate compressed air supply (up to 8 bar)

## Integration Steps

### 1. Prepare Custom Components
- 3D print or fabricate the custom bracket (`MPZ-30.stl`)
- 3D print or fabricate the custom fingers (`MPZ30_fingers.stl`)
- Ensure all mounting hardware is available

### 2. Finger Installation
1. Attach the custom fingers to the Schunk MPZ-30 gripper
2. Use M3x0.5 screws for secure attachment
3. Verify proper finger alignment and movement
4. Test finger clearance during open/close operations

### 3. Bracket Mounting
1. Mount the custom bracket to the Meca500 robot flange
2. Use M3x0.5 screws for secure attachment
3. Ensure bracket is properly aligned with robot coordinate system

### 4. Gripper Attachment
1. Attach the Schunk MPZ-30 gripper to the custom bracket
2. Use M4x0.7 screws for secure mounting
3. Orient the gripper at 90 degrees relative to the flange, facing down
4. Verify secure mounting and proper clearance

### 5. Pneumatic Connections
1. Install M5 threaded barb fittings (included with MPM500) on MPM500 output ports
2. Install M3 threaded barb fittings (purchased separately) on gripper ports A and B
3. Connect air input line to MPM500 pneumatic module
4. Connect gripper port A to MPM500 port 1 using pneumatic cable
5. Connect gripper port B to MPM500 port 2 using pneumatic cable
6. Test pneumatic connections for leaks

### 6. System Testing
1. Power on the Meca500 and MPM500 systems
2. Test gripper open/close operations using the Meca500 web interface
3. Verify proper gripping force and repeatability
4. Calibrate gripper positions if necessary

## Sample Code

### Basic Gripper Operations

```robotics
// Initialize gripper in open position
GripperOpen

// Move to approach position
MovePose(215.813, 1.282, 144.232, 20.74, 82.846, -19.853)

// Move to pick position
MoveLin(214.355, 1.239, 108.308, 138.4, 86.206, -138.008)

// Close gripper and wait for pneumatic actuation
GripperCloseDelay(1)

// Lift object
MoveLin(214.355, 1.239, 150.0, 138.4, 86.206, -138.008)

// Move to place position
MovePose(300.0, 100.0, 150.0, 0, 180, 0)

// Lower to place
MoveLin(300.0, 100.0, 108.0, 0, 180, 0)

// Open gripper and wait
GripperOpenDelay(1)

// Retract
MoveLin(300.0, 100.0, 150.0, 0, 180, 0)
```

### Three-Finger Centric Gripping Sequence

```robotics
// Initialize system
GripperOpen
Delay(0.5)

// Approach cylindrical object
MovePose(215.813, 1.282, 144.232, 20.74, 82.846, -19.853)

// Center over object
MoveLin(214.355, 1.239, 108.308, 138.4, 86.206, -138.008)

// Close fingers for centric grip
GripperCloseDelay(1)

// Verify grip by slight lift
MoveLin(214.355, 1.239, 110.0, 138.4, 86.206, -138.008)

// Continue with manipulation task
```

### Web Interface Testing

Use the Meca500 web interface to test gripper operations:
1. Navigate to the I/O section
2. Test gripper open command
3. Test gripper close command
4. Verify pneumatic response and timing

## Troubleshooting

### Common Issues

1. **Gripper not responding**
   - Check pneumatic connections to ports A and B
   - Verify MPM500 output configuration
   - Ensure adequate air pressure (up to 8 bar)
   - Check M3 and M5 threaded barb fittings

2. **Insufficient gripping force**
   - Check air pressure settings (up to 8 bar maximum)
   - Verify gripper finger alignment
   - Inspect for pneumatic leaks at fittings
   - Ensure proper cable routing

3. **Positioning errors**
   - Recalibrate robot tool center point (TCP)
   - Verify bracket mounting alignment
   - Check for mechanical play in M4x0.7 mounting screws
   - Validate 90-degree gripper orientation

4. **Fingers not closing concentrically**
   - Check finger attachment with M3x0.5 screws
   - Verify finger STL fabrication quality
   - Inspect gripper mechanism for obstructions

## Maintenance

### Regular Maintenance Tasks
- Inspect pneumatic connections for leaks
- Clean gripper fingers and contact surfaces
- Verify mounting screw torque (M3, M4)
- Test gripper force and repeatability
- Check air pressure regulation

### Replacement Parts
- Custom fingers (STL available for reprinting)
- M3x0.5 and M4x0.7 mounting screws
- M3 and M5 threaded barb fittings
- Pneumatic cables (1/16" ID or 4mm OD)
- O-rings and seals (consult Schunk documentation)

## Technical Support

For additional support and technical questions:
- [Mecademic Support Portal](https://support.mecademic.com)
- [Schunk Technical Documentation](https://schunk.com)

## Files Included

| File | Description | Size |
|------|-------------|------|
| `MPZ-30.stl` | Custom mounting bracket for Meca500 flange | TBD |
| `MPZ30_fingers.stl` | Custom three-finger grippers | TBD |

## Related Documentation

- [Meca500 User Manual](https://www.mecademic.com/resources/documentation)
- [MPM500 Pneumatic Module Documentation](https://www.mecademic.com/resources/documentation)
- [Schunk MPZ-30 Technical Data](https://schunk.com/products/gripping-systems/pneumatic-grippers)

## Performance Notes

### Advantages of Three-Finger Centric Design
- Superior centering capability for round objects
- Even force distribution around object perimeter
- Self-centering action reduces positioning requirements
- Excellent for handling delicate or irregularly shaped items

### Application Considerations
- Ideal for cylindrical objects (tubes, bottles, components)
- Suitable for fragile items requiring gentle handling
- Excellent repeatability for precision assembly tasks
- Compact design minimizes workspace interference