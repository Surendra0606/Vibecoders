// frontend/src/components/MapComponent.js
// This component displays the interactive Leaflet map, showing real-time
// crowd density and sentiment data from Firestore.

import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet'; 
import { collection, onSnapshot, query, orderBy, limit } from "firebase/firestore";
import { db } from '../firebaseConfig'; // Import the Firestore database instance

// IMPORTANT: Import L from 'leaflet' directly in this component if you use L.divIcon
import L from 'leaflet'; 

// Define a default position for the map (center of Bengaluru)
const DEFAULT_MAP_POSITION = [12.9716, 77.5946];
const DEFAULT_MAP_ZOOM = 13;

// Define the approximate geographical bounds for Bengaluru
// This will restrict the map from panning outside these coordinates.
const BENGALURU_BOUNDS = [
  [12.8, 77.4], // South-West coordinates (min lat, min lon)
  [13.1, 77.8]  // North-East coordinates (max lat, max lon)
];

// Define the minimum zoom level allowed.
// This prevents users from zooming out too far and seeing areas outside Bengaluru.
const MIN_ALLOWED_ZOOM = 12; // A zoom level of 12 or 11 usually keeps Bengaluru in view

// --- Component for Map Resizing ---
// This component uses the useMap hook to access the Leaflet map instance
// and calls invalidateSize() after a short delay, which is critical for
// ensuring the map renders correctly when its container's size is determined
// by CSS or dynamic layout.
function MapFix() {
  const map = useMap(); // Get the Leaflet map instance

  useEffect(() => {
    // A small delay often helps ensure the container has rendered with its final size
    const timer = setTimeout(() => {
      map.invalidateSize(); // Tell Leaflet to recalculate its size based on its container
      console.log("Map invalidateSize() called."); // Debugging log
    }, 250); // Increased delay to 250ms for more robustness

    return () => clearTimeout(timer); // Clean up the timer if component unmounts
  }, [map]); // Re-run if map instance changes (though it typically won't)

  return null; // This component doesn't render anything itself
}
// --- End MapFix Component ---


const MapComponent = () => { 
  const [crowdData, setCrowdData] = useState([]); // State to store crowd density data
  const [sentimentData, setSentimentData] = useState([]); // State to store sentiment data
  const [loadingMapData, setLoadingMapData] = useState(true); // Loading state for map data

  // useEffect hook to fetch and listen for real-time updates on crowd data
  useEffect(() => {
    // Create a Firestore query: target 'crowd_data' collection, order by timestamp (descending), limit to 50 latest.
    const q = query(collection(db, "crowd_data"), orderBy("timestamp", "desc"), limit(50));
    
    // onSnapshot sets up a real-time listener. It triggers every time data in the query changes.
    const unsubscribe = onSnapshot(q, (snapshot) => {
      // Process the snapshot to get only the latest data point for each unique location.
      // This prevents multiple markers for the same location if data is generated frequently.
      const latestCrowd = {};
      snapshot.docs.forEach(doc => {
        const data = doc.data();
        // Ensure timestamp is a valid object before accessing .seconds
        const docTimestamp = data.timestamp && data.timestamp.seconds ? data.timestamp.seconds : 0;
        const currentLatestTimestamp = latestCrowd[data.location_name] && latestCrowd[data.location_name].timestamp.seconds ? latestCrowd[data.location_name].timestamp.seconds : -1;

        if (!latestCrowd[data.location_name] || docTimestamp > currentLatestTimestamp) {
          latestCrowd[data.location_name] = { id: doc.id, ...data };
        }
      });
      setCrowdData(Object.values(latestCrowd)); // Update React state with the latest crowd data
      setLoadingMapData(false); // Data loaded
    }, (error) => {
      console.error("Error fetching crowd data:", error);
      setLoadingMapData(false); // Stop loading even on error
    });

    return () => unsubscribe(); // Cleanup the listener when the component unmounts to prevent memory leaks
  }, []); // Empty dependency array means this effect runs only once on component mount

  // useEffect hook to fetch and listen for real-time updates on sentiment data
  useEffect(() => {
    const q = query(collection(db, "sentiment_data"), orderBy("timestamp", "desc"), limit(50));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      // --- CHANGE HERE: Directly map all docs, no longer filtering for latest per location ---
      const allRecentSentiment = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setSentimentData(allRecentSentiment); // Set all fetched sentiment data
    }, (error) => {
      console.error("Error fetching sentiment data:", error);
    });
    return () => unsubscribe(); // Cleanup the listener
  }, []);

  // Helper function to determine the color of the crowd density circle based on density value
  const getDensityColor = (density) => {
    if (density >= 0.8) return 'red';    // High density
    if (density >= 0.6) return 'orange';   // Medium density
    return 'green';                      // Low density
  };

  // Helper function to determine the emoji for sentiment
  const getSentimentEmoji = (sentiment) => {
    if (sentiment === 'POSITIVE') return '😁'; // Smiling face for happy
    if (sentiment === 'NEGATIVE') return '😞'; // Sad face for sad
    return '😐'; // Neutral face for neutral or error
  };

  return (
    <MapContainer 
      center={DEFAULT_MAP_POSITION} 
      zoom={DEFAULT_MAP_ZOOM} 
      className="map-container"
      maxBounds={BENGALURU_BOUNDS} // Restrict map panning to Bengaluru bounds
      minZoom={MIN_ALLOWED_ZOOM}   // Prevent zooming out too far
      whenReady={(map) => { // Keep whenReady to handle potential resizes if parent's height changes
        map.target.invalidateSize();
      }}
    >
      <MapFix /> {/* CRITICAL: Add this component inside MapContainer */}

      {/* TileLayer defines the base map tiles (e.g., OpenStreetMap) */}
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
      />

      {loadingMapData && crowdData.length === 0 && sentimentData.length === 0 ? (
            // Display a loading overlay if no data has been loaded yet
            <div className="map-loading-overlay">
              <div className="map-loading-message">
                Initializing Map...
              </div>
            </div>
          ) : null}

      {/* Display Crowd Data as Circles */}
      {crowdData.map((data) => (
        // Circle component represents crowd density. Radius scales with density.
        <Circle
          key={data.id}
          center={[data.latitude, data.longitude]}
          radius={data.simulated_density * 2000} // Radius in meters, scales with density
          pathOptions={{
            color: getDensityColor(data.simulated_density), // Border color
            fillColor: getDensityColor(data.simulated_density), // Fill color
            fillOpacity: 0.5 // Semi-transparent fill
          }}
        >
          {/* Popup displayed when the circle is clicked */}
          <Popup>
            <div className="popup-title">{data.location_name}</div>
            <div className="popup-text">Density: <span className="popup-bold">{data.simulated_density.toFixed(2)}</span></div>
            <div className="popup-small-text">Updated: {data.timestamp ? new Date(data.timestamp.seconds * 1000).toLocaleTimeString() : 'N/A'}</div>
          </Popup>
        </Circle>
      ))}

      {/* Display Sentiment Data as Custom Markers (Emojis) */}
      {sentimentData.map((data) => (
        // Marker component for sentiment. Using L.divIcon for custom HTML content (emoji).
        <Marker
          key={`sentiment-${data.id}`}
          // Provide fallback coordinates if latitude/longitude are missing from data
          position={[data.latitude || DEFAULT_MAP_POSITION[0], data.longitude || DEFAULT_MAP_POSITION[1]]}
          icon={L.divIcon({
            className: 'custom-sentiment-marker', 
            // HTML content for the marker: an emoji. Added inline style for larger emoji size.
            html: `<div style="font-size: 28px; text-align: center; line-height: 1; filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.5));">${getSentimentEmoji(data.sentiment_score)}</div>`,
            iconSize: [28, 28], // Size of the emoji icon container
            iconAnchor: [14, 14], // Anchor point of the icon (center)
          })}
        >
          <Popup>
            <div className="popup-title">{data.location_name}</div>
            <div className="popup-text">Sentiment: <span className="popup-bold">{data.sentiment_score}</span></div>
            <div className="popup-small-text mt-1">"{data.text_content}"</div>
            <div className="popup-small-text">Updated: {data.timestamp ? new Date(data.timestamp.seconds * 1000).toLocaleTimeString() : 'N/A'}</div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapComponent;
