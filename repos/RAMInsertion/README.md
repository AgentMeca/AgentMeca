# Demo: Force-Guided RAM Insertion with ATI Net F/T Sensor and Meca500

This demo shows how to perform force-guided insertion (e.g., memory module or pin insertion) using an ATI Net F/T sensor and a Meca500 robot.

## Prerequisites
- A Meca500 robot connected to the network.
- An ATI Net F/T sensor (e.g., Nano17) on the network (default IP: `192.168.0.101`).
- Python 3.7 or later
- Python packages:
  ```bash
  pip install mecademicpy
  ```

## Configuration
1. **Sensor IP**: In `main.py` and in `NetFT.py`, update the IP address if your sensor uses a different one.
2. **Robot IP**: Modify the `MoveThread.connect(address)` call in `main.py` to match your robot’s IP.

## Directory Contents
- `main.py`: Orchestrates the insertion sequence using two threaded classes:
  - `ClickDetection`: monitors force sensor for a click event
  - `MoveThread`: drives the robot motion until click detection
- `forceFunctions.py`: Defines `MoveThread`, `FindSurface`, and `ClickDetection` classes.
- `NetFT.py`: Interfaces with the ATI Net F/T sensor over UDP/RDT.
- `ThreadTests.py`: Example script to test force/stop detection and motion threads.

## Running the Demo
1. **First Insertion**:
   ```bash
   python main.py
   ```
   - Robot executes an offline program, moves to a start joint position.
   - On reaching insertion point, threads start:
     - `ClickDetection` waits for a force drop (click)
     - `MoveThread` advances robot until sensor signals stop
   - Sequence repeats for a second insertion point.
2. **Test Threads Only**:
   ```bash
   python ThreadTests.py
   ```

Press `Ctrl+C` to abort; threads will exit cleanly and robot will disconnect.

## Troubleshooting
- **Sensor timeouts**: Ensure the sensor’s RDT port (49152) is reachable.
- **No click detected**: Adjust `max_force`/`force_delta` parameters in `main.py` and `forceFunctions.py`.
- **Robot motion issues**: Verify `mecademicpy` and robot firmware are compatible.
