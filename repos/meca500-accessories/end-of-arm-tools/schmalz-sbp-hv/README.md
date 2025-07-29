# Schmalz SBP-HV 2 04 7 Basic Ejector Integration

Integration guide for the Schmalz SBP-HV 2 04 7 basic ejector vacuum generator with Mecademic Meca500 robots for vacuum-based pick-and-place applications.

## Overview

The Schmalz SBP-HV 2 04 7 is a compact, lightweight basic ejector with plastic housing designed for decentralized vacuum supply in highly dynamic processes. This integration provides efficient vacuum generation for end-of-arm tooling applications with the Meca500 robot system.

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Model** | Schmalz SBP-HV 2 04 7 |
| **Type** | Basic ejector vacuum generator |
| **Housing Material** | Plastic |
| **Power Gradation** | Six levels |
| **Design** | Compact, lightweight |
| **Application** | Decentralized vacuum supply |

## Required Components

### Hardware
- Meca500 Robot (firmware 8.1.6 or above)
- MPM500 Pneumatic Module
- Schmalz SBP-HV 2 04 7 Basic Ejector
- Schmalz suction cup (application specific)
- Nozzle cartridge
- Custom mounting bracket (see STL files)
- M4x0.7 screws (x4) for bracket-to-ejector mounting
- M3x0.5 screws (x4) for bracket-to-Meca500 mounting
- M5 threaded barb fittings (included with MPM500) OR push-to-connect fittings
- G1/8"-F threaded barb fittings (purchased separately)
- 1/16 inch ID or 4mm OD pneumatic cables
- Compressed air supply

### Software
- Mecademic Robot Programming Interface
- Meca500 firmware 8.1.6 or above
- 3D printer for custom bracket (optional if fabricated elsewhere)

## Prerequisites

Before beginning the integration, ensure you have:
1. Reviewed the [Meca500 User Manual](https://www.mecademic.com/resources/documentation)
2. Reviewed the [MPM500 User Manual](https://www.mecademic.com/resources/documentation)
3. Completed the [MPM500 installation guide](https://support.mecademic.com/knowledge-base/how-to-install-and-operate-the-mpm500-pneumatic-module)
4. Verified MPM500 installation and proper operation
5. Downloaded and prepared the custom mounting bracket STL files
6. Selected appropriate suction cup for your application

## Integration Steps

### 1. Prepare Custom Components
- 3D print or fabricate the custom mounting bracket (STL provided by Mecademic)
- Ensure all mounting hardware is available
- Select appropriate Schmalz suction cup for application

### 2. Install Nozzle Cartridge
1. Install the appropriate nozzle cartridge in the Schmalz ejector
2. Ensure proper cartridge seating and alignment
3. Verify cartridge is compatible with your application requirements

### 3. Bracket Installation
1. Mount the custom bracket to the Meca500 robot flange
2. Use M3x0.5 screws (x4) for secure attachment
3. Ensure bracket is properly aligned with robot coordinate system
4. Verify adequate clearance for ejector and suction cup

### 4. Ejector Mounting
1. Attach the Schmalz SBP-HV ejector to the custom bracket
2. Use M4x0.7 screws (x4) for secure mounting
3. Ensure proper orientation for optimal performance
4. Verify secure mounting and proper clearance

### 5. Suction Cup Installation
1. Install the selected Schmalz suction cup to the ejector
2. Ensure proper connection and sealing
3. Verify suction cup orientation and clearance
4. Test manual cup compression if applicable

### 6. Pneumatic Connections
1. Install M5 threaded barb fittings on MPM500 (included) or use push-to-connect fittings
2. Install G1/8"-F threaded barb fittings on ejector (purchased separately)
3. Connect compressed air supply to MPM500 IN port
4. Connect pneumatic cable from MPM500 output to ejector air input
5. Connect vacuum line from ejector to MPM500 vacuum port (if applicable)
6. Test all pneumatic connections for leaks

### 7. System Testing
1. Power on the Meca500 and MPM500 systems
2. Test ejector operation using the Meca500 web interface
3. Execute `GripperClose` command to activate vacuum
4. Execute `GripperOpen` command to deactivate vacuum
5. Verify vacuum generation and release timing
6. Check for air leaks in the system

## Sample Code

### Basic Vacuum Operations

```robotics
// Initialize vacuum system (gripper open = no vacuum)
GripperOpen

// Move to approach position above object
MovePose(200.0, 0.0, 150.0, 0, 180, 0)

// Move down to object surface
MoveLin(200.0, 0.0, 100.0, 0, 180, 0)

// Activate vacuum (gripper close = vacuum on)
GripperClose
Delay(0.5)  // Allow time for vacuum to stabilize

// Lift object
MoveLin(200.0, 0.0, 150.0, 0, 180, 0)

// Move to place position
MovePose(300.0, 100.0, 150.0, 0, 180, 0)

// Lower to place position
MoveLin(300.0, 100.0, 105.0, 0, 180, 0)

// Release vacuum (gripper open = vacuum off)
GripperOpen
Delay(0.5)  // Allow time for release

// Retract
MoveLin(300.0, 100.0, 150.0, 0, 180, 0)
```

### Pick-and-Place with Vacuum Verification

```robotics
// Enhanced vacuum pick sequence
MovePose(200.0, 0.0, 150.0, 0, 180, 0)

// Approach object carefully
MoveLin(200.0, 0.0, 102.0, 0, 180, 0)

// Activate vacuum
GripperClose
Delay(0.8)  // Extended delay for vacuum buildup

// Test lift (verify grip before full lift)
MoveLin(200.0, 0.0, 108.0, 0, 180, 0)
Delay(0.3)

// Full lift if grip is secure
MoveLin(200.0, 0.0, 150.0, 0, 180, 0)

// Transport to destination
MovePose(300.0, 100.0, 150.0, 0, 180, 0)

// Lower for placement
MoveLin(300.0, 100.0, 105.0, 0, 180, 0)

// Controlled release
GripperOpen
Delay(0.5)

// Confirm release and retract
MoveLin(300.0, 100.0, 150.0, 0, 180, 0)
```

### Web Interface Testing

Use the Meca500 web interface for initial testing:
1. Navigate to the I/O section
2. Execute `GripperClose` command to activate vacuum
3. Execute `GripperOpen` command to deactivate vacuum
4. Verify ejector response and timing
5. Monitor vacuum performance and stability

## Vacuum System Optimization

### Power Gradation Settings
The SBP-HV ejector features six power gradation levels:
- Level 1: Minimum vacuum for light objects
- Level 6: Maximum vacuum for heavy objects
- Adjust level based on object weight and surface characteristics

### Nozzle Cartridge Selection
- **Small Nozzles**: High vacuum, low flow rate
- **Large Nozzles**: Lower vacuum, high flow rate
- Select cartridge based on application requirements

## Troubleshooting

### Common Issues

1. **Insufficient Vacuum**
   - Check compressed air pressure and quality
   - Verify all pneumatic connections for leaks
   - Ensure proper nozzle cartridge selection
   - Check suction cup condition and fit

2. **Vacuum Not Releasing**
   - Verify MPM500 control signals
   - Check for blockages in pneumatic lines
   - Ensure proper `GripperOpen` command execution
   - Inspect ejector for debris or contamination

3. **Object Dropping During Transport**
   - Increase vacuum stabilization delay
   - Check suction cup seal quality
   - Verify object surface cleanliness
   - Consider different suction cup design
   - Adjust power gradation level

4. **System Not Responding**
   - Verify firmware version compatibility
   - Check MPM500 configuration and status
   - Test web interface commands manually
   - Verify compressed air supply and quality

### Performance Issues

1. **Slow Vacuum Buildup**
   - Check air supply pressure
   - Verify nozzle cartridge condition
   - Inspect for air leaks in system
   - Consider higher power gradation level

2. **Poor Object Release**
   - Check for vacuum line restrictions
   - Verify proper vacuum breaking mechanism
   - Ensure adequate release delay timing
   - Inspect suction cup for damage

## Maintenance

### Regular Maintenance Tasks
- Inspect pneumatic connections for leaks
- Clean suction cup surfaces regularly
- Check compressed air filter and water trap
- Verify ejector nozzle cartridge condition
- Test vacuum performance periodically
- Clean ejector housing and connections

### Replacement Parts
- Nozzle cartridges (application specific)
- Suction cups (various sizes and materials)
- Pneumatic fittings (M5, G1/8"-F threaded barb fittings)
- Pneumatic cables (1/16" ID or 4mm OD)
- O-rings and seals

### Preventive Maintenance Schedule
- **Daily**: Visual inspection of connections and suction cups
- **Weekly**: Clean suction cups and check for damage
- **Monthly**: Test vacuum performance and check air quality
- **Quarterly**: Inspect and replace pneumatic filters
- **Annually**: Replace nozzle cartridges and critical seals

## Performance Specifications

### Vacuum Performance
- **Vacuum Level**: Dependent on nozzle cartridge and air pressure
- **Flow Rate**: Variable based on power gradation setting
- **Response Time**: Fast activation/deactivation
- **Energy Efficiency**: Optimized for dynamic processes

### Application Suitability
- **Lightweight Objects**: Excellent performance with appropriate settings
- **Smooth Surfaces**: Optimal for non-porous materials
- **Dynamic Applications**: Designed for high-speed pick-and-place
- **Compact Workspaces**: Minimal footprint design

## Technical Support

For additional support and technical questions:
- [Mecademic Support Portal](https://support.mecademic.com)
- [Schmalz Technical Documentation](https://www.schmalz.com)
- [Schmalz Vacuum Technology Support](https://www.schmalz.com/en/support/)

## Files Included

| File | Description | Source |
|------|-------------|---------|
| Custom Bracket STL | Mounting bracket for Meca500 flange | Mecademic (free to use) |

## Related Documentation

- [Meca500 User Manual](https://www.mecademic.com/resources/documentation)
- [MPM500 Pneumatic Module Documentation](https://www.mecademic.com/resources/documentation)
- [MPM500 Installation Guide](https://support.mecademic.com/knowledge-base/how-to-install-and-operate-the-mpm500-pneumatic-module)
- [Schmalz SBP-HV Product Page](https://www.schmalz.com/en/vacuum-technology-for-automation/vacuum-components/vacuum-generators/basic-ejectors/)

## Application Examples

### Suitable Applications
- Electronic component handling
- Small part assembly
- Packaging operations
- Material sorting
- Clean room applications
- Food and pharmaceutical handling (with appropriate components)

### Performance Advantages
- **Compact Design**: Minimal space requirements
- **Energy Efficient**: Optimized vacuum generation
- **Fine Power Control**: Six gradation levels
- **Fast Response**: Quick activation and release
- **Reliable Operation**: Proven vacuum technology

## Safety Considerations

- Ensure adequate vacuum release before object placement
- Verify object security before rapid movements
- Monitor compressed air quality and pressure
- Use appropriate personal protective equipment
- Follow all robot safety protocols during integration
- Maintain clear work area during vacuum operations