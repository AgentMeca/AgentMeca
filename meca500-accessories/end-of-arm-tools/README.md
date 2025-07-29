# End-of-Arm Tools

Complete integration guides for pneumatic grippers, vacuum systems, and tool changers compatible with the Meca500 robot. These implementations provide detailed setup instructions, wiring diagrams, and sample code for automated pick-and-place operations.

## Available Integrations

### Pneumatic Grippers

#### [SMC JMHZ2 12D Air Gripper](smc-jmhz2-12d/)
- **Type**: Pneumatic parallel gripper
- **Specifications**: 12mm bore, 6mm stroke, 23.3N closing force
- **Features**: Custom STL files for bracket and fingers, web interface control
- **Applications**: Small part handling, precision picking

#### [Schunk MPZ 30 Pneumatic Gripper](schunk-mpz-30/)
- **Type**: 3-finger centric gripper
- **Specifications**: 55N closing force, 3mm stroke per jaw, 0.01mm repeatability
- **Features**: Centered gripping, high repeatability
- **Applications**: Cylindrical parts, centered gripping operations

#### [Schunk MPG Plus-25 Pneumatic Gripper](schunk-mpg-plus-25/)
- **Type**: Parallel pneumatic gripper
- **Specifications**: 3mm stroke, 38N closing force, 0.06 kg weight
- **Features**: Compact design, lightweight construction
- **Applications**: Light-duty applications, space-constrained setups

#### [Schunk KGG 60 Pneumatic Gripper](schunk-kgg-60/)
- **Type**: Large stroke pneumatic gripper
- **Specifications**: 20mm stroke, 45N closing force
- **Features**: Large stroke capability, custom STL files
- **Applications**: Medium-duty applications, variable part sizes

### Vacuum Systems

#### [Bimba (Vaccon) Venturi Vacuum Pump](bimba-vaccon-venturi/)
- **Type**: Venturi vacuum generator
- **Specifications**: JS-150-AA4 model, 80 psi operating pressure
- **Features**: Two pneumatic circuit configurations, compact design
- **Applications**: Suction cup operations, flat surface handling

#### [Schmalz SBP-HV 2 04 7 Basic Ejector](schmalz-sbp-hv/)
- **Type**: Basic vacuum ejector
- **Specifications**: Plastic housing, six power gradation levels
- **Features**: Adjustable vacuum levels, basic ejector functionality
- **Applications**: Light vacuum applications, educational setups

### Tool Changers

#### [Kosmek SWR0010 Pneumatic Tool Changer](kosmek-swr0010/)
- **Type**: Pneumatic tool changer
- **Specifications**: 5-micron repeatability, 1 million cycle life, 0.5-1 kg payload
- **Features**: High repeatability, long operational life
- **Applications**: Automated tool changing, flexible manufacturing

## Common Integration Components

### Hardware Requirements
- **Meca500 Robot**: 6-axis collaborative robot arm
- **MPM500 Pneumatic Module**: Provides compressed air control and distribution
- **Pneumatic Connections**: Quick-connect fittings and tubing
- **Custom Mounting**: 3D-printable STL files (where available)

### Software Requirements
- **MecaConnect**: Web-based robot interface
- **Python/C# Libraries**: Programming interfaces for custom applications
- **Network Configuration**: Ethernet connectivity for robot communication

### Pneumatic System Setup
1. **Air Supply**: 4-10 bar (58-145 psi) compressed air
2. **MPM500 Configuration**: Connect pneumatic module to robot controller
3. **Tubing Installation**: Route pneumatic lines to end-of-arm tool
4. **Control Programming**: Implement gripper commands in robot programs

## Programming Examples

Each integration includes sample code demonstrating:
- **Gripper Control**: Open/close commands with timing
- **Pick and Place**: Complete automated sequences
- **Status Monitoring**: Grip confirmation and error handling
- **Web Interface**: Browser-based control examples

## Getting Started

1. **Select Integration**: Choose the appropriate end-of-arm tool for your application
2. **Hardware Setup**: Follow the specific integration guide for mechanical installation
3. **Pneumatic Connection**: Connect air supply and configure MPM500 module
4. **Software Configuration**: Install required libraries and configure network settings
5. **Testing**: Run provided examples to verify proper operation

## Support Resources

- [Mecademic Knowledge Base](https://support.mecademic.com/knowledge-base/mecanetwork)
- [MPM500 Documentation](https://support.mecademic.com/knowledge-base/mpm500-pneumatic-module)
- [Meca500 User Manual](https://support.mecademic.com/knowledge-base/meca500-user-manual)
- [MecaConnect Interface Guide](https://support.mecademic.com/knowledge-base/mecaconnect-web-interface)

## Technical Support

For integration assistance or troubleshooting:
- Review the specific integration guide for your tool
- Check pneumatic connections and air pressure
- Verify network configuration and robot connectivity
- Consult the troubleshooting sections in each integration guide