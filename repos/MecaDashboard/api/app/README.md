# MecaDashboard API App Package

This package defines the Flask application instance and its routes for robot management.

## Prerequisites
- Python 3.7 or later
- `flask`, `mecademicpy`

## Package Structure
- `__init__.py`: Initializes the Flask `app` and a `robotList` dictionary.
- `routes.py`: Implements HTTP endpoints under `/`.
- `app.py`: Imports the Flask `app` for `flask run`.

## API Endpoints
- GET `/`              : Health check (returns `Mecademic`).
- POST `/registerRobot`: Register and connect to a robot (JSON `{ ip: string }`).
- GET `/getStatus`     : Query robot status by `ip` query param.
- POST `/moveJoints`   : Stub endpoint that echoes joint command JSON.

## Usage
Run the Flask server from the parent `api` folder:
```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```
