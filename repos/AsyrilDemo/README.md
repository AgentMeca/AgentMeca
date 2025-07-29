# Asyril EyePlus & Meca500 Python Demo

This demo shows how to integrate an Asyril EyePlus vision camera with a Meca500 robot to pick parts from a feeder and place them into a vial rack.

## Prerequisites
- A Meca500 robot connected to the network (default IP: `192.168.1.100`).
- An Asyril EyePlus camera connected to the network (default IP: `192.168.1.50`, port `7171`).
- Python 3.7 or later installed.
- Python dependencies installed:
  ```bash
  pip install mecademicpy
  ```

## Configuration
1. **Robot IP**: In `main.py`, update the `robot.Connect('192.168.1.100')` line if your robot uses a different IP.
2. **Camera IP/Port**: In `main.py` and test scripts, update `camera.connect('192.168.1.50', 7171)` to match your camera settings.
3. **Positions**: All TCP reference frames and Cartesian/joint positions are defined in `positions.py`.

## Demo Scripts
1. **Test camera vision** – run `get_part_test.py` to verify the EyePlus can detect parts:
   ```bash
   python get_part_test.py
   ```
   - Enter `quit` to stop production and exit.
2. **Test pick operation** – run `pick_part_test.py` to pick a single part from the feeder:
   ```bash
   python pick_part_test.py
   ```
   - Enter `quit` to stop.
3. **Full automation** – run `main.py` to continuously pick parts and place them in successive rack positions:
   ```bash
   python main.py
   ```

## What the Full Demo Does
1. Connects to camera and robot, homes the robot, and moves to a safe start position.
2. Starts EyePlus production and enters a loop:
   - Queries camera for a part's XYR (X, Y, rotation) position.
   - Moves robot above the part, picks it with the gripper, and retracts.
   - Moves to the next vial position and places the part.
   - When the rack is full, empties the rack back onto the feeder and restarts.
3. Stops production and disconnects cleanly on termination.

## Troubleshooting
- **Connection errors**: Verify IP addresses and network cables.
- **Camera status != 200**: Check the camera recipe ID and make sure no other client is connected.
- **Robot errors**: Ensure the robot is in normal mode and not in recovery. Check that mecademicpy is up to date.

---
_Based on the structure of the Meca500 C# QuickStart example._
