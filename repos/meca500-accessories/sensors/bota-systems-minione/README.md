# Bota Systems MiniONE Pro / Medusa Pro Force Sensor Integration

Integration system for connecting Bota Systems force/torque sensors with Mecademic Meca500 robots via EtherCAT communication. Supports both MiniONE Pro and Medusa Pro sensor models for high-precision force feedback applications.

This repository provides complete integration documentation for:
- **MiniONE Pro FT Sensor**: Compact 6-axis force/torque sensor
- **Medusa Multi-axis Force Torque Sensor**: Advanced force sensing solution
- **EtherCAT Communication**: Real-time sensor data via Beckhoff PLC integration
- **TwinCAT3 Configuration**: Complete setup and configuration guide

## System Overview

### Components Required

#### Hardware Components
- **Robot**: Meca500 industrial robot (firmware 8.1.6 or higher)
- **PLC Controller**: Beckhoff C6015-0010 Ultra-compact Industrial PC
- **Sensors**: Bota Systems MiniONE Pro or Medusa Pro force/torque sensor
- **Power Supply**: 24V DC power supply for PLC
- **Cables**: RJ45 Ethernet cables for EtherCAT communication
- **Mounting**: Sensor mounting hardware and brackets

#### Software Components
- **TwinCAT3**: Beckhoff automation software for EtherCAT configuration
- **Windows OS**: Required for TwinCAT3 operation
- **ESI Files**: Electronic data sheets for sensor configuration
- **Sensor Software**: Bota Systems configuration and monitoring tools

## Sensor Specifications

### MiniONE Pro Specifications
| Parameter | Value | Unit |
|-----------|-------|------|
| **Force Range** | ±200 | N |
| **Torque Range** | ±6 | Nm |
| **Sampling Rate** | Up to 1000 | Hz |
| **Weight** | 110 | g |
| **Dimensions** | 48 x 32 | mm |
| **Protection Rating** | IP67 | - |
| **Communication** | EtherCAT | - |
| **Power via PoE** | Yes | - |

### Medusa Pro Specifications
| Parameter | Value | Unit |
|-----------|-------|------|
| **Force Range** | ±500 | N |
| **Torque Range** | ±20 | Nm |
| **Sampling Rate** | Up to 1000 | Hz |
| **Weight** | 280 | g |
| **Dimensions** | 63 x 40 | mm |
| **Protection Rating** | IP67 | - |
| **Communication** | EtherCAT | - |
| **IMU Integration** | Yes | - |

### Key Features
- **Plug & Work Design**: Simplified installation and configuration
- **High Sensitivity**: Precise force and torque measurements
- **Real-time Communication**: EtherCAT for deterministic data transmission
- **Inertia Compensation**: Automatic compensation for sensor mass effects
- **Temperature Compensation**: Stable operation across temperature ranges
- **Overload Protection**: Mechanical and electronic overload protection

## System Architecture

### Communication Flow
```
Meca500 Robot ←→ EtherCAT ←→ Beckhoff PLC ←→ Bota Sensor
     ↕                                    ↕
Control Application ←→ TwinCAT3 Runtime ←→ Sensor Data
```

### Network Configuration
- **EtherCAT Network**: High-speed real-time communication
- **Sensor Address**: Configurable EtherCAT slave address
- **Data Rate**: Up to 1 kHz force/torque data streaming
- **Latency**: < 1ms for real-time control applications

## Installation Guide

### 1. Hardware Setup

#### Sensor Mounting
1. **Install Mounting Bracket**: Attach sensor mounting bracket to robot flange
2. **Mount Sensor**: Secure sensor using M3 screws (MiniONE) or M4 screws (Medusa)
3. **Cable Management**: Route sensor cable with appropriate strain relief
4. **PoE Connection**: Connect sensor to PoE adapter for power and data

#### PLC Installation
1. **Mount PLC**: Install Beckhoff C6015-0010 in control cabinet
2. **Power Connection**: Connect 24V DC power supply to PLC
3. **Network Cables**: Connect EtherCAT cables between robot, PLC, and sensor
4. **Grounding**: Ensure proper electrical grounding for all components

### 2. Meca500 Configuration

#### EtherCAT Activation
```python
# Switch Meca500 to EtherCAT mode
robot.SwitchToEtherCAT()

# Verify EtherCAT status
status = robot.GetEtherCATStatus()
print(f"EtherCAT Status: {status}")
```

#### Network Settings
- **EtherCAT Port**: Use dedicated EtherCAT port on Meca500
- **IP Configuration**: EtherCAT operates at datalink layer (no IP required)
- **Cycle Time**: Configure for 1ms cycle time for optimal performance

### 3. TwinCAT3 Configuration

#### Initial Setup
1. **Install TwinCAT3**: Download and install TwinCAT3 from Beckhoff
2. **License Activation**: Activate TwinCAT3 runtime license
3. **Create Project**: Start new TwinCAT3 project for sensor integration

#### Device Configuration
1. **Scan Devices**: Use TwinCAT3 to scan EtherCAT network
2. **Add Sensor**: Import sensor ESI file and add to configuration
3. **Configure Parameters**: Set sampling rate, filters, and coordinate frames
4. **Activate Configuration**: Download and activate configuration to PLC

#### ESI File Installation
```
1. Download ESI files from Bota Systems website
2. Copy files to TwinCAT3 ESI directory:
   C:\TwinCAT\3.1\Config\Io\EtherCAT\
3. Restart TwinCAT3 to load new device descriptions
4. Sensor will appear in device catalog
```

### 4. Sensor Configuration

#### Basic Parameters
```xml
<!-- Example TwinCAT3 configuration for MiniONE Pro -->
<Device>
    <Type>Bota MiniONE Pro</Type>
    <SamplingRate>1000</SamplingRate>
    <ForceRange>200</ForceRange>
    <TorqueRange>6</TorqueRange>
    <CoordinateFrame>Tool</CoordinateFrame>
    <Units>
        <Force>Newton</Force>
        <Torque>NewtonMeter</Torque>
    </Units>
</Device>
```

#### Advanced Settings
- **Filter Configuration**: Configure low-pass filters for noise reduction
- **Calibration Matrix**: Load factory calibration or perform custom calibration
- **Coordinate Transformation**: Set tool coordinate frame transformation
- **Alarm Limits**: Configure force/torque limit monitoring

## Programming Interface

### TwinCAT3 PLC Programming

#### Data Structure
```pascal
TYPE ST_ForceData :
STRUCT
    Fx : REAL;      // Force X-axis [N]
    Fy : REAL;      // Force Y-axis [N]
    Fz : REAL;      // Force Z-axis [N]
    Tx : REAL;      // Torque X-axis [Nm]
    Ty : REAL;      // Torque Y-axis [Nm]
    Tz : REAL;      // Torque Z-axis [Nm]
    Status : WORD;  // Sensor status word
    Counter : DWORD;// Data counter
END_STRUCT
END_TYPE
```

#### Basic Reading
```pascal
PROGRAM ForceSensorRead
VAR
    fbSensor : FB_BotaSensor;
    ForceData : ST_ForceData;
    bEnable : BOOL := TRUE;
END_VAR

// Read sensor data
fbSensor(bEnable := bEnable, stForceData => ForceData);

// Display force values
LogMessage := CONCAT('Force X: ', REAL_TO_STRING(ForceData.Fx));
LogMessage := CONCAT(LogMessage, ' Force Y: ');
LogMessage := CONCAT(LogMessage, REAL_TO_STRING(ForceData.Fy));
```

### ADS Communication

#### C# Integration
```csharp
using TwinCAT.Ads;

public class BotaSensorInterface
{
    private TcAdsClient adsClient;
    private uint forceDataHandle;
    
    public bool Connect(string amsNetId)
    {
        try
        {
            adsClient = new TcAdsClient();
            adsClient.Connect(amsNetId, 851); // PLC port
            
            // Create variable handle for force data
            forceDataHandle = adsClient.CreateVariableHandle("MAIN.ForceData");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Connection failed: {ex.Message}");
            return false;
        }
    }
    
    public ForceData ReadForceData()
    {
        var data = new ForceData();
        var buffer = new byte[32]; // Force data structure size
        
        adsClient.Read(forceDataHandle, buffer);
        
        // Parse binary data to force structure
        data.Fx = BitConverter.ToSingle(buffer, 0);
        data.Fy = BitConverter.ToSingle(buffer, 4);
        data.Fz = BitConverter.ToSingle(buffer, 8);
        data.Tx = BitConverter.ToSingle(buffer, 12);
        data.Ty = BitConverter.ToSingle(buffer, 16);
        data.Tz = BitConverter.ToSingle(buffer, 20);
        
        return data;
    }
}
```

#### Python Integration
```python
import pyads

class BotaSensorReader:
    def __init__(self, ams_net_id, ams_port=851):
        self.plc = pyads.Connection(ams_net_id, ams_port)
        self.connected = False
    
    def connect(self):
        try:
            self.plc.open()
            self.connected = True
            print("Connected to TwinCAT3 PLC")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def read_force_data(self):
        if not self.connected:
            return None
        
        try:
            # Read force data structure
            force_data = self.plc.read_by_name("MAIN.ForceData", pyads.PLCTYPE_REAL * 6)
            
            return {
                'Fx': force_data[0],
                'Fy': force_data[1],
                'Fz': force_data[2],
                'Tx': force_data[3],
                'Ty': force_data[4],
                'Tz': force_data[5]
            }
        except Exception as e:
            print(f"Read error: {e}")
            return None
    
    def disconnect(self):
        if self.connected:
            self.plc.close()
            self.connected = False
```

## Application Examples

### 1. Force Monitoring Application
```pascal
PROGRAM ForceMonitoring
VAR
    fbSensor : FB_BotaSensor;
    ForceData : ST_ForceData;
    ForceThreshold : REAL := 50.0;  // 50N threshold
    bForceAlarm : BOOL;
END_VAR

// Read sensor continuously
fbSensor(bEnable := TRUE, stForceData => ForceData);

// Monitor force magnitude
ForceMagnitude := SQRT(ForceData.Fx*ForceData.Fx + 
                       ForceData.Fy*ForceData.Fy + 
                       ForceData.Fz*ForceData.Fz);

// Check threshold
bForceAlarm := ForceMagnitude > ForceThreshold;

IF bForceAlarm THEN
    // Trigger safety response
    LogError('Force threshold exceeded!');
END_IF
```

### 2. Compliant Motion Control
```python
# Python example for compliant motion
class CompliantMotion:
    def __init__(self, robot, sensor_reader):
        self.robot = robot
        self.sensor = sensor_reader
        self.compliance_gain = 0.1  # mm/N
    
    def compliant_move(self, target_position, compliance_axes=[True, True, False]):
        """Execute compliant movement with force feedback"""
        
        while not self.at_target(target_position):
            # Read current force
            force_data = self.sensor.read_force_data()
            
            if force_data:
                # Calculate compliance correction
                correction = [0, 0, 0]
                
                if compliance_axes[0]:  # X-axis compliance
                    correction[0] = -force_data['Fx'] * self.compliance_gain
                
                if compliance_axes[1]:  # Y-axis compliance  
                    correction[1] = -force_data['Fy'] * self.compliance_gain
                
                if compliance_axes[2]:  # Z-axis compliance
                    correction[2] = -force_data['Fz'] * self.compliance_gain
                
                # Apply corrected velocity
                adjusted_velocity = self.calculate_velocity(target_position, correction)
                self.robot.MoveVelTrf(adjusted_velocity)
            
            time.sleep(0.01)  # 100 Hz control loop
```

### 3. Assembly Operation
```pascal
PROGRAM AssemblyControl
VAR
    fbSensor : FB_BotaSensor;
    ForceData : ST_ForceData;
    InsertionForce : REAL := 15.0;    // Target insertion force
    LateralForceLimit : REAL := 5.0;  // Lateral force limit
    bAssemblyActive : BOOL;
    AssemblyState : INT;              // Assembly state machine
END_VAR

CASE AssemblyState OF
    0: // Approach
        // Move towards assembly point
        IF ForceData.Fz > 2.0 THEN  // Contact detected
            AssemblyState := 1;
        END_IF
    
    1: // Insertion
        // Apply controlled insertion force
        IF ForceData.Fz > InsertionForce THEN
            // Reduce insertion velocity
        ELSIF ForceData.Fz < InsertionForce THEN
            // Increase insertion velocity
        END_IF
        
        // Monitor lateral forces for alignment
        IF ABS(ForceData.Fx) > LateralForceLimit OR 
           ABS(ForceData.Fy) > LateralForceLimit THEN
            AssemblyState := 2; // Correction needed
        END_IF
    
    2: // Lateral correction
        // Apply lateral compliance
        // Return to insertion when aligned
        
END_CASE
```

## Calibration Procedures

### Factory Calibration
1. **Load Calibration Matrix**: Import factory calibration from sensor EEPROM
2. **Verify Accuracy**: Test calibration with known weights and torques
3. **Document Settings**: Record calibration parameters for reference

### Custom Calibration
```python
def custom_calibration(sensor_reader, calibration_weights):
    """Perform custom sensor calibration"""
    
    calibration_data = []
    
    for weight in calibration_weights:
        print(f"Apply {weight}N weight and press Enter...")
        input()
        
        # Read multiple samples
        samples = []
        for i in range(100):
            force_data = sensor_reader.read_force_data()
            if force_data:
                samples.append(force_data['Fz'])
            time.sleep(0.01)
        
        # Calculate average
        avg_reading = sum(samples) / len(samples)
        calibration_data.append((weight, avg_reading))
    
    # Calculate calibration factor
    calibration_factor = calculate_linear_fit(calibration_data)
    print(f"Calibration factor: {calibration_factor}")
    
    return calibration_factor
```

### Bias Removal
```pascal
PROGRAM BiasCalibration
VAR
    fbSensor : FB_BotaSensor;
    ForceData : ST_ForceData;
    BiasSamples : ARRAY[1..100] OF ST_ForceData;
    BiasData : ST_ForceData;
    SampleCount : INT;
    bCalibrating : BOOL;
END_VAR

// Collect bias samples
IF bCalibrating AND SampleCount < 100 THEN
    SampleCount := SampleCount + 1;
    BiasSamples[SampleCount] := ForceData;
    
    IF SampleCount = 100 THEN
        // Calculate bias averages
        BiasData.Fx := 0; BiasData.Fy := 0; BiasData.Fz := 0;
        BiasData.Tx := 0; BiasData.Ty := 0; BiasData.Tz := 0;
        
        FOR i := 1 TO 100 DO
            BiasData.Fx := BiasData.Fx + BiasSamples[i].Fx;
            BiasData.Fy := BiasData.Fy + BiasSamples[i].Fy;
            BiasData.Fz := BiasData.Fz + BiasSamples[i].Fz;
            BiasData.Tx := BiasData.Tx + BiasSamples[i].Tx;
            BiasData.Ty := BiasData.Ty + BiasSamples[i].Ty;
            BiasData.Tz := BiasData.Tz + BiasSamples[i].Tz;
        END_FOR
        
        BiasData.Fx := BiasData.Fx / 100.0;
        BiasData.Fy := BiasData.Fy / 100.0;
        BiasData.Fz := BiasData.Fz / 100.0;
        BiasData.Tx := BiasData.Tx / 100.0;
        BiasData.Ty := BiasData.Ty / 100.0;
        BiasData.Tz := BiasData.Tz / 100.0;
        
        bCalibrating := FALSE;
    END_IF
END_IF
```

## Advanced Features

### IMU Integration (Medusa Pro)
The Medusa Pro includes integrated IMU for enhanced sensing capabilities:

```python
def read_imu_data(sensor_reader):
    """Read IMU data from Medusa Pro sensor"""
    
    imu_data = sensor_reader.plc.read_by_name("MAIN.IMUData", pyads.PLCTYPE_REAL * 9)
    
    return {
        'acceleration': {
            'x': imu_data[0],
            'y': imu_data[1], 
            'z': imu_data[2]
        },
        'angular_velocity': {
            'x': imu_data[3],
            'y': imu_data[4],
            'z': imu_data[5]
        },
        'orientation': {
            'roll': imu_data[6],
            'pitch': imu_data[7],
            'yaw': imu_data[8]
        }
    }
```

### Inertia Compensation
Automatic compensation for sensor mass effects:

```pascal
FUNCTION InertiaCompensation : ST_ForceData
VAR_INPUT
    RawForce : ST_ForceData;
    Acceleration : ARRAY[1..3] OF REAL;
    AngularVelocity : ARRAY[1..3] OF REAL;
END_VAR
VAR
    CompensatedForce : ST_ForceData;
    SensorMass : REAL := 0.11;  // MiniONE Pro mass in kg
END_VAR

// Compensate for gravitational and inertial forces
CompensatedForce.Fx := RawForce.Fx - SensorMass * Acceleration[1];
CompensatedForce.Fy := RawForce.Fy - SensorMass * Acceleration[2];
CompensatedForce.Fz := RawForce.Fz - SensorMass * (Acceleration[3] + 9.81);

// Compensate for angular effects on torque measurements
// (Implementation depends on specific sensor geometry)

InertiaCompensation := CompensatedForce;
```

## Troubleshooting

### Common Issues

#### EtherCAT Communication Problems
1. **Check Cable Connections**: Verify all EtherCAT cables are properly connected
2. **Verify Network Topology**: Ensure proper EtherCAT chain configuration
3. **Check Device Status**: Use TwinCAT3 to verify all devices are operational
4. **Timing Issues**: Verify cycle time configuration matches network capability

#### Sensor Configuration Issues
```python
def diagnose_sensor_issues(sensor_reader):
    """Diagnostic function for sensor problems"""
    
    # Check communication
    force_data = sensor_reader.read_force_data()
    if force_data is None:
        print("ERROR: No sensor communication")
        return False
    
    # Check for stuck values
    readings = []
    for i in range(10):
        data = sensor_reader.read_force_data()
        if data:
            readings.append(data['Fz'])
        time.sleep(0.1)
    
    if len(set(readings)) == 1:
        print("WARNING: Sensor readings appear stuck")
        return False
    
    # Check for unrealistic values
    for reading in readings:
        if abs(reading) > 1000:  # Unrealistic force
            print(f"WARNING: Unrealistic force reading: {reading}N")
            return False
    
    print("Sensor diagnostics passed")
    return True
```

#### Data Quality Issues
1. **Noise**: Configure appropriate low-pass filters in TwinCAT3
2. **Drift**: Perform bias calibration regularly
3. **Overload**: Check for mechanical damage after overload events
4. **Temperature Effects**: Allow sensor warm-up time for stable readings

### Performance Optimization

#### High-Frequency Operation
```pascal
// Optimize for 1kHz operation
VAR_GLOBAL
    CycleTime : TIME := T#1MS;  // 1ms cycle time
    SensorData : ST_ForceData;
END_VAR

// Main control task running at 1kHz
TASK MainTask(INTERVAL := CycleTime, PRIORITY := 1);

PROGRAM MainControl
    // Sensor reading optimized for minimal latency
    fbSensor(bEnable := TRUE, stForceData => SensorData);
    
    // Process data immediately
    ProcessForceData(SensorData);
END_PROGRAM
```

## Safety Considerations

### Force Monitoring
- **Overload Protection**: Implement software force limits below hardware limits
- **Emergency Stop**: Provide accessible emergency stop functionality
- **Monitoring Systems**: Continuous monitoring of force and torque values
- **Fail-Safe Behavior**: Define safe behavior for communication failures

### Installation Safety
- **Proper Mounting**: Ensure secure sensor mounting to prevent detachment
- **Cable Management**: Use appropriate strain relief and cable protection
- **Electrical Safety**: Follow proper grounding and isolation procedures
- **Environmental Protection**: Verify IP67 rating is maintained after installation

## Support Resources

### Documentation
- [Bota Systems Technical Documentation](https://www.botasys.com/documentation)
- [TwinCAT3 User Manual](https://infosys.beckhoff.com/english.php?content=../content/1033/tc3_overview/index.html)
- [Mecademic EtherCAT Guide](https://support.mecademic.com/knowledge-base/ethercat)

### Software Downloads
- **TwinCAT3**: Available from Beckhoff website with free runtime license
- **ESI Files**: Download latest sensor ESI files from Bota Systems
- **Example Projects**: Complete TwinCAT3 projects available on request

### Support Contacts
- **Technical Support**: Bota Systems and Mecademic technical support teams
- **Integration Services**: Professional integration services available
- **Training**: Training courses available for TwinCAT3 and EtherCAT

This integration provides a robust, high-performance solution for force feedback applications with excellent real-time performance and comprehensive monitoring capabilities.