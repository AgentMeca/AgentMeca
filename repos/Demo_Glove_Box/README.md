This demo showcases an end-to-end glove-box application where a Meca500 robot picks colored vials from a rack, loads them into a centrifuge, and returns them—all via a PyQt5-based UI.

## Prerequisites
- One or two Meca500 robots on the network (default IPs: `192.168.0.100`, `192.168.0.101`).
- Python 3.7 or later
- Install dependencies:
  ```bash
  pip install mecademicpy requests PyQt5 scipy
  ```

## Configuration
1. **Robot IPs**: In `Application/mainApp.py`, adjust the `Robot().Connect(...)` calls to match your robot IPs.
2. **Rack & Centrifuge Points**: Use `structure.txt` as a guide. In the **Setup** window you can define pick/place coordinates for rack slots and centrifuge positions, or load defaults.
3. **Requirements**: All Python dependencies are listed in `requirements.txt`.

## Components & Usage
1. **Backend Logic** (`backend/`): Defines `MainRack` and `Centrifuge` classes to track positions/status. No standalone server—used directly by the Application.
2. **Frontend UI** (`frontend/`): PyQt5 `.ui` and Python files for three windows:
   - **Main Window**: Connect, select vials, and start auto mode
   - **Setup Window**: Define pick/place coordinates
   - **Progress Window**: Simulate centrifuge processing
3. **Application** (`Application/`): Glue code that launches the UI and drives the robot via `mecademicpy`.
   ```bash
   python Application/mainApp.py
   ```
4. **Tests** (`tests/`): Simple scripts to verify custom widgets and rotation math.
   ```bash
   python tests/pyqtTests.py
   python tests/rot_test.py
   ```

## High-Level Workflow
1. Launch the **Application** GUI.
2. In **Setup**, define rack and centrifuge positions or load defaults.
3. In **Main**, connect to robot(s), select vials, and press **Auto Mode**.
4. Robot picks vial, loads/unloads centrifuge; **Progress** window simulates processing.
5. At completion, vials return to rack.

## Troubleshooting
- **Connection errors**: Check robot IP addresses, ensure no firewall blocks.
- **UI fails to launch**: Verify PyQt5 is installed.
- **Unexpected coordinate behavior**: Re-calibrate in **Setup** or update `structure.txt`.
