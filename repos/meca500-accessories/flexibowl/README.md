# FlexiBowl® Integration

Integration plugins for communicating with FlexiBowl® feeder systems through Mecademic robots using C# or Python. No additional license required.

This repository provides two complete implementations:
- **C# Plugin**: Full-featured class with UDP/TCP support and friendly command interface
- **Python Plugin**: Simple TCP-based functions for basic FlexiBowl operations

## Communication Protocol

FlexiBowl uses eSCL (Ethernet Serial Command Language) based on MOONS' Serial Command Language (SCL). Commands and responses are encapsulated in packets using standard Ethernet hardware and TCP/IP stacks.

### Packet Format

**Sending Commands:**
- Format: `header SCL_string <cr>`
- Header: Binary [0,7] (two bytes)
- SCL String: ASCII encoded characters
- Terminator: ASCII carriage return (13)

**Example:** Sending "RV"
```
header "RV" <cr>
0 7 82 86 13
```

**Receiving Responses:**
Response to "RV" would be "RV=103<cr>" formatted as:
```
header "RV=103" <cr>
0 7 82 86 61 49 48 51 13
```

## Command Reference

| Action | Description | Command |
|--------|-------------|---------|
| MOVE | Moves the feeder with current parameters | QX2 |
| MOVE-FLIP | Moves the feeder and activates Flip simultaneously | QX3 |
| MOVE-BLOW-FLIP | Moves the feeder and activates Flip and blow simultaneously | QX4 |
| MOVE-BLOW | Moves the feeder and activates blow simultaneously | QX5 |
| SHAKE | Shakes the feeder with current parameters | QX6 |
| LIGHT ON | Turn light on | QX7 |
| LIGHT OFF | Turn light off | QX8 |
| FLIP | Activate flip mechanism | QX10 |
| BLOW | Activate blow mechanism | QX9 |
| QUICK_EMPTYING | Quick emptying option | QX11 |
| RESET_ALARM | Reset alarm and enable motor | QX12 |
| ALARM_STATUS | Check alarm status | AL |

## Implementation Files

### C# Implementation
- **File**: `csharp/FlexiBowl_Plugin.cs` 
- **Features**: UDP/TCP dual protocol, friendly commands, alarm monitoring, movement tracking
- **Documentation**: See `csharp/README.md` for detailed API reference

### Python Implementation  
- **File**: `python/flexibowl_plugin.py`
- **Features**: TCP communication, alarm checking, movement commands with polling
- **Documentation**: See `python/README.md` for detailed API reference

## Quick Start

### C# Usage
```csharp
// Initialize with TCP protocol support
Flexibowl_Plugin fb = new Flexibowl_Plugin(true);

// Check device status
bool isOk = fb.CheckAlarmStatus("192.168.0.161");

// Execute movement with friendly command
string result = fb.FlexibowlFriendly("192.168.0.161", "MOVE");

// Clean up resources
fb.Flexibowl_Close();
```

### Python Usage
```python
from flexibowl_plugin import move_flb1, in_allarm

# Check alarm status
if in_allarm("192.168.0.161"):
    # Execute movement command
    success = move_flb1("192.168.0.161", "MOVE")
    if success:
        print("Movement completed successfully")
```

## Network Configuration

| Parameter | C# (UDP) | C# (TCP) | Python (TCP) |
|-----------|----------|----------|--------------|
| **Remote Port** | 7775 | 7776 | 7776 |
| **Local Port** | 7777 | N/A | N/A |
| **Timeout** | 500ms | 2000ms | 2000ms |
| **Protocol** | UDP | TCP | TCP |

## Setup Requirements

### C# Requirements
- .NET Framework 4.0+
- System.Net.Sockets namespace
- System.Collections.Generic for command mapping
- Visual Studio or compatible C# IDE

### Python Requirements
- Python 3.x
- Standard library modules: `socket`, `time`, `sys`
- No external dependencies required