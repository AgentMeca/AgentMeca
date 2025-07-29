# AddRobotDialog Component

A modal dialog used to register a new robot by IP address.

## Usage
```jsx
import AddRobotDialog from './components/CardHolder/AddRobotDialog';

<AddRobotDialog
  open={isDialogOpen}
  onSubmit={handleRegister}
  onClose={handleClose}
/>
```

## Props
- `open` (bool): Controls dialog visibility.
- `onSubmit` (func): Called with robot IP when user confirms.
- `onClose` (func): Called when dialog is dismissed.

## Notes
Uses Material-UI or custom styling. Parent handles actual registration API call.
