# RobotCard Component

Displays the status and controls for a single robot in the dashboard.

## Usage
```jsx
import RobotCard from './components/RobotCard';

<RobotCard
  ip={robot.ip}
  status={robot.status}
  onMove={handleMove}
/>
```

## Props
- `ip` (string): Robot IP address.
- `status` (object): `{ Activated, Homed, Error }`.
- `onMove` (func): Callback to send joint/move commands.

## Notes
Fetches real-time status from backend. Styles defined in `RobotCard.css`.
