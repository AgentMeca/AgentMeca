# AddCardButton Component

A button component that opens the AddRobotDialog to register a new robot.

## Usage
```jsx
import AddCardButton from './components/CardHolder/AddCardButton';

<AddCardButton onClick={openDialog} />
```

## Props
- `onClick`: Function to invoke when the button is clicked.

## Notes
Styled as part of the CardHolder grid. Triggers `AddRobotDialog` in parent.
