# StatusBar Component

A horizontal bar of status indicators for a robot or system event.

## Usage
```jsx
import StatusBar from './components/StatusBar';

<StatusBar statuses={[true, false, true]} />
```

## Props
- `statuses`: Array of booleans; each renders a `StatusLed` on (true) or off (false).

## Notes
Use `StatusBar` within `RobotCard` or global app header.
