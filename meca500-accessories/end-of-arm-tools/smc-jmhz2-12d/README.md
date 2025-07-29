# SMC JMHZ2 12D Air Gripper Integration

Integration guide for the SMC JMHZ2 12D compact parallel pneumatic gripper with Mecademic Meca500 robots.

## Overview

The SMC JMHZ2 12D is a compact, double-acting pneumatic gripper designed for precision pick-and-place applications. This integration provides complete setup instructions, hardware requirements, and sample code for seamless operation with the Meca500 robot.

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Gripper Type** | Compact parallel, double-acting pneumatic |
| **Bore Size** | 12 mm |
| **Stroke per Jaw** | 6 mm |
| **Gripping Force (Open)** | 17.5 N per finger |
| **Gripping Force (Close)** | 23.3 N per finger |
| **Repeatability** | 0.01 mm |
| **Weight** | 0.65 kg |

## Required Components

### Hardware
- Meca500 Robot (firmware 8.1.6 or above)
- MPM500 Pneumatic Module
- SMC JMHZ2 12D Pneumatic Gripper
- Custom mounting bracket (see STL files)
- Custom gripper fingers (see STL files)
- M2 screws (for finger attachment)
- M3x0.5 screws (for bracket mounting)
- Pneumatic fittings (barb/push-to-connect)
- Pneumatic cables

### Software
- Mecademic Robot Programming Interface
- 3D printer for custom brackets and fingers (optional if fabricated elsewhere)

## Prerequisites

Before beginning the integration, ensure you have:
1. Reviewed the [Meca500 User Manual](https://www.mecademic.com/resources/documentation)
2. Reviewed the [MPM500 User Manual](https://www.mecademic.com/resources/documentation)
3. Verified MPM500 installation and proper operation
4. Downloaded and prepared the custom mounting hardware STL files

## Integration Steps

### 1. Prepare Custom Components
- 3D print or fabricate the custom bracket (`SMC_bracket.stl`)
- 3D print or fabricate the custom fingers (`SMC_fingers.stl`)
- Ensure all mounting hardware is available

### 2. Finger Installation
1. Attach the custom fingers to the SMC JMHZ2 12D gripper
2. Use M2 screws for secure attachment
3. Verify proper finger alignment and movement

### 3. Bracket Mounting
1. Mount the custom bracket to the Meca500 robot flange
2. Use M3x0.5 screws for secure attachment
3. Ensure bracket is properly aligned with robot coordinate system

### 4. Gripper Attachment
1. Attach the SMC JMHZ2 12D gripper to the custom bracket
2. Orient the gripper at 90 degrees as specified
3. Verify secure mounting and proper clearance

### 5. Pneumatic Connections
1. Connect barb or push-to-connect fittings to gripper pneumatic ports
2. Route pneumatic cables from MPM500 to gripper
3. Connect gripper ports to corresponding MPM500 output ports
4. Test pneumatic connections for leaks

### 6. System Testing
1. Power on the Meca500 and MPM500 systems
2. Test gripper open/close operations
3. Verify proper gripping force and repeatability
4. Calibrate gripper positions if necessary

## Sample Code

### Basic Gripper Operations

```robotics
// Move to approach position
MovePose(215.813, 1.282, 144.232, 20.74, 82.846, -19.853)

// Move to pick position
MoveLin(214.355, 1.239, 108.308, 138.4, 86.206, -138.008)

// Close gripper and wait
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

### Pick-and-Place Sequence

```robotics
// Initialize gripper in open position
GripperOpen

// Define approach position
MovePose(215.813, 1.282, 144.232, 20.74, 82.846, -19.853)

// Approach object
MoveLin(214.355, 1.239, 108.308, 138.4, 86.206, -138.008)

// Secure grip with delay for pneumatic actuation
GripperCloseDelay(1)

// Continue with pick-and-place sequence as needed
```

## Troubleshooting

### Common Issues

1. **Gripper not responding**
   - Check pneumatic connections
   - Verify MPM500 output configuration
   - Ensure adequate air pressure

2. **Insufficient gripping force**
   - Check air pressure settings
   - Verify gripper finger alignment
   - Inspect for pneumatic leaks

3. **Positioning errors**
   - Recalibrate robot tool center point (TCP)
   - Verify bracket mounting alignment
   - Check for mechanical play in connections

## Maintenance

### Regular Maintenance Tasks
- Inspect pneumatic connections for leaks
- Clean gripper fingers and contact surfaces
- Verify mounting screw torque
- Test gripper force and repeatability

### Replacement Parts
- Custom fingers (STL available for reprinting)
- M2 and M3 mounting screws
- Pneumatic fittings and cables
- O-rings and seals (consult SMC documentation)

## Technical Support

For additional support and technical questions:
- [Mecademic Support Portal](https://support.mecademic.com)
- [SMC Technical Documentation](https://www.smcpneumatics.com)

## Files Included

| File | Description | Size |
|------|-------------|------|
| `SMC_bracket.stl` | Custom mounting bracket for Meca500 flange | 36.9 KB |
| `SMC_fingers.stl` | Custom gripper fingers | 27.6 KB |

## Related Documentation

- [Meca500 User Manual](https://www.mecademic.com/resources/documentation)
- [MPM500 Pneumatic Module Documentation](https://www.mecademic.com/resources/documentation)
- [SMC JMHZ2 Series Technical Data](https://www.smcpneumatics.com)