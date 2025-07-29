# Demo: Well Plate & Cover Handling with Two Meca500 Robots

This demo uses two Meca500 robots to pick and place well plates and their covers in a coordinated workflow.

## Prerequisites
- Two Meca500 robots on the same network:
  - Default IPs in `main.py`: robot1 at `192.168.0.100`, robot2 at `192.168.0.101`
- Python 3.7 or later
- `mecademicpy` library installed:
  ```bash
  pip install mecademicpy
  ```

## Configuration
1. **Robot IPs**: Update the `Connect(...)` calls in `main.py` if your robots use different IP addresses.
2. **Movement Functions**: High-level pick/place routines are defined as:
   - `pick1/place1`, `pick2/place2`: handle two different plate stations
   - `pick_cover*/place_cover*`: handle cover operations
   - `push_corner*`: perform corner pushing actions for proper placement
3. **Workflow Description**: See `structure.txt` for an overview of the two-robot sequence.

## Running the Demo
Simply execute:
```bash
python main.py
```
This will:
1. Home both robots and set initial velocities
2. Enter an infinite loop:
   - Robot2 picks and places the plate cover
   - Robot1 picks a plate and moves it to a target location
   - Both robots perform return (pick-back) actions
   - Additional corner-push steps ensure accurate placement

Press `Ctrl+C` to terminate the demo. Robots will stop safely.

## Troubleshooting
- **Connection failures**: Verify robot IPs and network setup.
- **Unexpected behavior**: Check that all pick/place coordinates match your physical setup.
- **Library errors**: Ensure `mecademicpy` is up to date and compatible.
