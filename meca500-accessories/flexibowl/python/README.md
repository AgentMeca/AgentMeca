# Python FlexiBowl Plugin

A Python module providing TCP communication functions for FlexiBowl feeder systems.

## Features

- **TCP Communication**: Direct socket connection on port 7776
- **Alarm Monitoring**: Hex-to-binary alarm status checking
- **Movement Commands**: Friendly command names with automatic completion tracking
- **Status Polling**: Different polling strategies based on command type
- **Debug Output**: Built-in print statements for troubleshooting

## Functions

### `in_allarm(ip)`
Checks if the FlexiBowl device is in alarm state.

**Parameters:**
- `ip` (str): IP address of the FlexiBowl device

**Returns:**
- `bool`: `True` if operational (no alarms), `False` if in alarm or connection failed

**Protocol Details:**
- Sends "AL" command via TCP
- Extracts hex alarm data from `data[5:]`
- Converts hex to 16-bit binary for bit analysis
- Returns `False` if any alarm bits are set (decimal > 0)

**Packet Format:**
```python
MESSAGE = chr(0) + chr(7) + "AL" + chr(13)  # NULL + 7 + "AL" + CR
```

### `move_flb1(ip, command)`
Sends movement commands to the FlexiBowl device.

**Parameters:**
- `ip` (str): IP address of the FlexiBowl device  
- `command` (str): Friendly command name (see Command Reference)

**Returns:**
- `bool`: `True` if command executed successfully, `False` otherwise

**Command Processing:**
1. Maps friendly command to SCL protocol command
2. Sends command and waits for "%" response (command accepted)
3. Polls device status until operation completes
4. Uses different status checking methods based on command type

## Command Reference

| Friendly Command | SCL Command | Description |
|-----------------|-------------|-------------|
| "MOVE" | "QX2" | Basic movement |
| "MOVE FLIP" | "QX3" | Move with flip action |
| "MOVE BLOW FLIP" | "QX4" | Move with blow and flip |
| "MOVE BLOW" | "QX5" | Move with blow action |
| "SHAKE" | "QX6" | Shake the bowl |
| "LIGHT ON" | "QX7" | Turn on illumination |
| "LIGHT OFF" | "QX8" | Turn off illumination |
| "FLIP" | "QX10" | Flip action only |
| "BLOW" | "QX9" | Blow action only |
| "QUICK EMPTY OPTION" | "QX11" | Quick empty sequence |
| *Invalid* | "QX60" | Used for unrecognized commands |

## Movement Completion Logic

When a command returns "%" (indicating acceptance), the function polls for completion:

### IO Status Commands (QX11, QX10, QX4, QX3)
```python
MESSAGE = chr(0) + chr(7) + "IO" + chr(13)
moving = data[12:-1]  # Extract busy status
if int(moving) == 1:  # Not busy = operation complete
    break
```

### SC Status Commands (All Others)
```python
MESSAGE = chr(0) + chr(7) + "SC" + chr(13) 
moving = data[7:-2]   # Extract completion status
if int(moving) == 0:  # Operation completed
    break
```

**Polling Interval:** 100ms between status checks

## Error Handling

- **Connection Errors**: Caught with generic `except:` blocks
- **Timeout**: 2-second socket timeout prevents hanging
- **Invalid Commands**: Mapped to "QX60" which device will reject
- **Debug Output**: Print statements show sent/received messages

## Usage Examples

### Basic Movement
```python
from flexibowl_plugin import move_flb1, in_allarm

# Check alarm status first
if in_allarm("192.168.0.161"):
    print("Device OK")
    
    # Execute movement
    success = move_flb1("192.168.0.161", "MOVE")
    if success:
        print("Movement completed")
    else:
        print("Movement failed")
else:
    print("Device in alarm state")
```

### Multiple Operations
```python
# Turn on light
move_flb1("192.168.0.161", "LIGHT ON")

# Perform move with flip
move_flb1("192.168.0.161", "MOVE FLIP")

# Turn off light  
move_flb1("192.168.0.161", "LIGHT OFF")
```

## Network Configuration

- **Protocol**: TCP/IP
- **Port**: 7776
- **Timeout**: 2 seconds
- **Buffer Size**: 1024 bytes
- **Packet Format**: [0,7] + ASCII_COMMAND + [13]

## Debug Output

Both functions include debug print statements:
- Message sent to device
- Response received from device
- Alarm status hex/binary data (in `in_allarm`)
- Status polling data (in `move_flb1`)

## Dependencies

- `socket` (standard library)
- `time` (standard library) 
- `sys` (standard library)

## Error Conditions

- **"Not Connected1"**: Alarm check connection failed
- **"Not Connected2"**: Movement command connection failed
- **Function returns False**: Command rejected or execution failed
- **Invalid command**: Automatically mapped to "QX60"