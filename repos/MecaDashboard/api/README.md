# MecaDashboard API (Flask Backend)

This folder contains the Flask-based API server that the React frontend uses to communicate with one or more Meca500 robots.

## Prerequisites
- Python 3.7 or later
- Install dependencies:
  ```bash
  cd MecaDashboard/api
  pip install -r requirement.txt
  ```

## Configuration
1. Edit `requirement.txt` to add any additional Python packages.
2. (Optional) Adjust Flask host/port via environment variables.

## Available Endpoints
- `GET /` : Health check (returns `Mecademic`).
- `POST /registerRobot` : Register and connect to a robot.
  - JSON body: `{ "ip": "<robot_ip>" }`
  - Response: `{ "Connection": true|false }`
- `GET /getStatus?ip=<robot_ip>` : Get robot status.
  - Response: `{ "Activated": bool, "Homed": bool, "Error": bool }`
- `POST /moveJoints` : (Stub) Echoes posted JSON joint values.

## Running the Server
```bash
cd MecaDashboard/api
export FLASK_APP=app.py        # or set FLASK_APP=app.py on Windows
flask run --host=0.0.0.0 --port=5000
```
The API will be available at `http://localhost:5000/`.
