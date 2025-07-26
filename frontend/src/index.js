// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client'; // Use ReactDOM.createRoot for React 18+
import './index.css'; // Import global CSS (now contains all styling)
import App from './App'; // Import the main App component
import reportWebVitals from './reportWebVitals'; // For performance monitoring

// Import Leaflet's core CSS - ESSENTIAL for map rendering
import 'leaflet/dist/leaflet.css'; 

// This is a crucial workaround for Leaflet's default icon paths in React applications.
// Without this, default map markers (like the blue pin) will not appear correctly.
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Use ReactDOM.createRoot for React 18+ to render the root component
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
