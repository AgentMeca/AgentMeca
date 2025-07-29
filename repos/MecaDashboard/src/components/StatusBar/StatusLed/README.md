# StatusLed Component

Renders a single LED indicator to show on/off status.

## Usage
```jsx
import StatusLed from './components/StatusBar/StatusLed';

<StatusLed active={true} />
```

## Props
- `active` (boolean): When `true`, LED appears green/on; when `false`, gray/off.

## Notes
Used by `StatusBar` to visualize multiple system or robot flags.
