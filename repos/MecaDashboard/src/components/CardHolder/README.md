# CardHolder Component

Container that displays a grid of robot cards, plus an Add Card button.

## Usage
```jsx
import CardHolder from './components/CardHolder';

function Dashboard() {
  return <CardHolder robots={robotList} />;
}
```

## Props
- `robots`: Array of robot objects to display as cards.

## Structure
- Renders each `RobotCard` child.
- Includes `AddCardButton` to register new robots via dialog.
