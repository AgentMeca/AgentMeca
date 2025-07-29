# MecaDashboard Frontend (React App)

This folder contains the React-based dashboard application for monitoring and controlling Meca500 robots.

## Prerequisites
- Node.js (v14+) and npm

## Installation
```bash
cd MecaDashboard
npm install
```

## Available Scripts
- `npm start` : Runs the app in development mode at [http://localhost:3000].
- `npm test`  : Launches the test runner.
- `npm run build`: Builds the app for production in the `build` folder.

## Project Structure
- `index.js`: Entry point that renders `<App />`.
- `App.js`   : Main container component.
- `components/`: Reusable UI components.

## Configuration
Modify API base URL in `src/App.js` (e.g., toggle backend connection flag or change `fetch` URLs).
