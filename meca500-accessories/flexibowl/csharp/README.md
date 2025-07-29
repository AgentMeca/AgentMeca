# C# FlexiBowl Plugin

A comprehensive C# class for communicating with FlexiBowl feeder systems via UDP/TCP protocols.

## Features

- **Dual Protocol Support**: UDP (port 7775) and TCP (port 7776) communication
- **Friendly Command Interface**: Use human-readable commands like "MOVE", "LIGHT ON"
- **Alarm Monitoring**: Check device alarm status with hex-to-binary conversion
- **Movement Completion Tracking**: Automatic polling for operation completion
- **Resource Management**: Proper connection cleanup and disposal

## Class Structure

### Constructor
```csharp
Flexibowl_Plugin()                    // Default UDP mode
Flexibowl_Plugin(bool useTcp)        // Protocol selection
```

### Core Methods

#### `Flexibowl(string ipAddress, string command)`
Sends raw SCL commands via UDP
- **Parameters**: IP address, SCL command (e.g., "QX2", "AL")
- **Returns**: Response string or error message
- **Protocol**: Creates packet with header [0,7] + command + CR(13)

#### `FlexibowlFriendly(string ipAddress, string friendlyCommand)`
Sends commands using friendly names
- **Parameters**: IP address, friendly command (e.g., "MOVE", "LIGHT ON")
- **Returns**: Response string or error message  
- **Command Mapping**: Translates friendly names to SCL commands

#### `CheckAlarmStatus(string ipAddress)`
Checks device alarm state via TCP
- **Parameters**: IP address
- **Returns**: `true` if no alarms, `false` if in alarm state
- **Logic**: Sends "AL" command, converts hex response to binary for error checking

#### `Flexibowl_Close()`
Releases network resources and closes connections

## Command Mapping

| Friendly Command | SCL Command | Description |
|-----------------|-------------|-------------|
| "MOVE" | "QX2" | Basic movement |
| "MOVE FLIP" | "QX3" | Move with flip |
| "MOVE BLOW FLIP" | "QX4" | Move with blow and flip |
| "MOVE BLOW" | "QX5" | Move with blow |
| "SHAKE" | "QX6" | Shake bowl |
| "LIGHT ON" | "QX7" | Turn on illumination |
| "LIGHT OFF" | "QX8" | Turn off illumination |
| "FLIP" | "QX10" | Flip mechanism |
| "BLOW" | "QX9" | Blow mechanism |
| "QUICK EMPTY OPTION" | "QX11" | Quick empty sequence |

## Movement Completion Logic

For commands that return "%" (motion in progress):

1. **Status Commands Used**:
   - `IO` command: For QX11, QX10, QX4, QX3 (checks busy signal)
   - `SC` command: For other movement commands (checks completion status)

2. **Polling Logic**:
   - IO status: Wait until `data[12:-1] == 1` (not busy)
   - SC status: Wait until `data[7:-2] == 0` (completed)
   - 100ms polling interval

## Error Handling

- Try-catch blocks around all network operations
- Timeout settings: 500ms (UDP), 2000ms (TCP)
- Proper resource disposal in finally blocks
- Exception details returned as strings

## Usage Example

```csharp
// Initialize with TCP protocol
Flexibowl_Plugin fb = new Flexibowl_Plugin(true);

// Check alarm status
bool isOk = fb.CheckAlarmStatus("192.168.0.161");
Console.WriteLine($"Status: {(isOk ? "OK" : "ALARM")}");

// Execute movement with friendly command
string result = fb.FlexibowlFriendly("192.168.0.161", "MOVE");
Console.WriteLine($"Result: {result}");

// Execute raw SCL command
string response = fb.Flexibowl("192.168.0.161", "QX7");

// Clean up resources
fb.Flexibowl_Close();
```

## Network Configuration

- **UDP Mode**: Port 7775, local port 7777
- **TCP Mode**: Port 7776
- **Timeouts**: 500ms (UDP), 2000ms (TCP)
- **Packet Format**: [0,7] + ASCII_COMMAND + [13]

## Dependencies

- System.Net.Sockets
- System.Text (for ASCII encoding)
- System.Collections.Generic (for command mapping)