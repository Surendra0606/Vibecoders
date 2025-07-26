// frontend/src/components/AlertsPanel.js
// This component displays a real-time list of threat alerts fetched from Firestore.

import React, { useState, useEffect } from 'react';
import { collection, onSnapshot, query, orderBy, limit } from "firebase/firestore";
import { db } from '../firebaseConfig'; // Import the Firestore database instance

const AlertsPanel = () => {
  const [alerts, setAlerts] = useState([]); // State to store the list of alerts

  useEffect(() => {
    // Create a Firestore query: target 'threat_alerts' collection,
    // order by timestamp (descending to show most recent first), limit to 10 latest alerts.
    const q = query(collection(db, "threat_alerts"), orderBy("timestamp", "desc"), limit(10));
    
    // onSnapshot sets up a real-time listener. It triggers every time data in the query changes.
    const unsubscribe = onSnapshot(q, (snapshot) => {
      // Map the Firestore documents to a more usable array of objects for React state.
      const newAlerts = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setAlerts(newAlerts); // Update the state
    }, (error) => {
      console.error("Error fetching alerts:", error);
    });

    return () => unsubscribe(); // Cleanup the listener when the component unmounts
  }, []); // Empty dependency array means this effect runs only once on component mount

  // Helper function to determine the CSS classes for an alert card based on its threat level.
  const getAlertCardStyle = (level) => {
    if (level === 'HIGH') return 'alert-card-high'; // Custom class for high severity
    if (level === 'MEDIUM') return 'alert-card-medium'; // Custom class for medium severity
    // Default style for 'LOW' or other levels
    return 'alert-card-low'; // Custom class for low severity
  };

  return (
    <div class="alerts-list-wrapper" style={{height:"200px", overflowY: 'scroll'}}> {/* Replaced Tailwind: space-y-4 */}
      {/* <h3 class="alert-panel-header">Live Alerts</h3> Replaced Tailwind: text-lg font-bold text-gray-800 mb-3 */}
      {alerts.length === 0 ? (
        // Display a message if there are no active alerts
        <p class="alerts-no-data-message">No recent alerts. Everything seems normal.</p> /* Replaced Tailwind: text-gray-500 text-sm */
      ) : (
        // Render the list of alerts.
        // max-h-80 and overflow-y-auto make the alert list scrollable if it gets too long.
        <div class="alerts-list-container custom-scrollbar"> {/* Replaced Tailwind: space-y-3 max-h-80 overflow-y-auto pr-2 */}
          {alerts.map(alert => (
            // Each alert is a card with styling based on its threat level
            <div key={alert.id} class={`alert-card ${getAlertCardStyle(alert.threat_level)}`}> {/* Replaced Tailwind: p-3 rounded-md shadow-sm border-l-4 border-red-500 bg-red-100 text-red-800 */}
                  {/* Alert type and location name */}
                  <p class="alert-card-title">🚨 {alert.threat_type} at {alert.location_name}</p> {/* Replaced Tailwind: font-semibold text-base mb-1 */}
                  {/* Threat level */}
                  <p class="alert-card-text">Level: <span class="alert-card-bold">{alert.threat_level}</span></p> {/* Replaced Tailwind: text-sm font-bold */}
                  {/* Detailed description of the alert */}
                  <p class="alert-card-small-text">{alert.details}</p> {/* Replaced Tailwind: text-xs mt-1 */}
                  {/* Timestamp of the alert */}
                  <p class="alert-card-small-text alert-card-timestamp">
                    {/* Convert Firestore Timestamp object to a readable local string */}
                    {alert.timestamp ? new Date(alert.timestamp.seconds * 1000).toLocaleString() : 'Loading...'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    };

    export default AlertsPanel;
