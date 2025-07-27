// frontend/src/components/CameraFeed.js
// This component displays a simulated camera feed by fetching an image URL
// from a specific Firestore document and updating it in real-time.

import React, { useState, useEffect } from 'react';
import { doc, onSnapshot } from "firebase/firestore";
import { db } from '../firebaseConfig'; // Import the Firestore database instance

const CameraFeed = () => {
  const [imageUrl, setImageUrl] = useState(''); // State to store the current image URL
  const [locationName, setLocationName] = useState(''); // State to store the camera's location name
  const [loading, setLoading] = useState(true); // State to indicate if the feed is loading

  useEffect(() => {
    // Listen to a specific Firestore document where the camera image URL is updated.
    // CRITICAL FIX: Ensure this ID matches the one used by the backend updater script.
    // The backend uses 'main_alert_camera_feed'.
    const docRef = doc(db, 'camera_feeds', 'main_alert_camera_feed'); 

    // onSnapshot sets up a real-time listener for this specific document.
    const unsubscribe = onSnapshot(docRef, (docSnap) => {
      if (docSnap.exists()) {
        console.log("Hiii");
        // If the document exists, extract the data and update the component's state.
        const data = docSnap.data();
        console.log(data);
        setImageUrl(data.image_url); // This is where the image URL is read
        setLocationName(data.location_name || 'Simulated Camera'); // Use a fallback name
        setLoading(false); // Loading is complete
      } else {
        // If the document does not exist, log a message and clear the image.
        console.log("No camera feed data found for 'main_alert_camera_feed'. Please ensure backend updater is running and writing to this ID.");
        setImageUrl(''); // Clear the image if no data
        setLoading(false); // Loading is complete even if there's an error
      }
    }, (error) => {
      // Log any errors that occur during fetching the document.
      console.error("Error fetching camera feed document:", error);
      setLoading(false); // Loading is complete even if there's an error
    });

    return () => unsubscribe(); // Cleanup the listener when the component unmounts
  }, []); // Empty dependency array means this effect runs only once on component mount


  console.log(imageUrl);
  
  return (
   
    <div class="camera-feed-container">
      <h3 class="camera-feed-header">Simulated Camera Feed</h3>
      <div class="camera-feed-content-wrapper">
        {loading ? (
          <div class="camera-feed-loading-message">
            Loading Camera Feed...
          </div>
        ) : imageUrl ? (
          <img
            src={imageUrl}
            alt={`Simulated camera feed from ${locationName}`}
            class="camera-feed-image"
          />
        ) : (
          <div class="camera-feed-no-feed-message">
            No Camera Feed Available
          </div>
        )}
        
        {locationName && (
          <div class="camera-feed-location-overlay">
            {locationName}
          </div>
        )}
        {imageUrl && ( // Only show LIVE tag if an image is actually loaded
          <div class="camera-feed-live-tag">
            LIVE
          </div>
        )}
      </div>
      <p class="camera-feed-description">This feed updates periodically to simulate real-time visuals.</p>
    </div>
  );
};

export default CameraFeed;
