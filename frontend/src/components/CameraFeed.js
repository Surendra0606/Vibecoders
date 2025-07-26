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
    // The backend script (sim_camera_feed_updater.py) writes to 'camera_feeds/demo_camera_1'.
    const docRef = doc(db, 'camera_feeds', 'demo_camera_1'); 
    
    // onSnapshot sets up a real-time listener for this specific document.
    const unsubscribe = onSnapshot(docRef, (docSnap) => {
      if (docSnap.exists()) {
        // If the document exists, extract the data and update the component's state.
        const data = docSnap.data();
        setImageUrl(data.image_url);
        setLocationName(data.location_name || 'Simulated Camera'); // Use a fallback name
        setLoading(false); // Loading is complete
      } else {
        // If the document does not exist, log a message and clear the image.
        console.log("No camera feed data found for 'demo_camera_1'. Please ensure backend updater is running.");
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

  return (
    <div class="camera-feed-container"> {/* Replaced Tailwind: space-y-4 */}
      <h3 class="camera-feed-header">Simulated Camera Feed</h3> {/* Replaced Tailwind: text-lg font-bold text-gray-800 mb-3 */}
      <div class="camera-feed-content-wrapper"> {/* Replaced Tailwind: bg-gray-200 rounded-lg overflow-hidden relative aspect-video */}
        {loading ? (
          // Display a loading message while the image is being fetched
          <div class="camera-feed-loading-message"> {/* Replaced Tailwind: w-full h-full flex items-center justify-center text-gray-600 text-sm */}
            Loading Camera Feed...
          </div>
        ) : imageUrl ? (
          // Display the image if imageUrl is available
          <img
            src={imageUrl}
            alt={`Simulated camera feed from ${locationName}`}
            class="camera-feed-image" /* Replaced Tailwind: w-full h-full object-cover object-center */
          />
        ) : (
          // Display a message if no camera feed is available
          <div class="camera-feed-no-feed-message"> {/* Replaced Tailwind: w-full h-full flex items-center justify-center text-gray-600 text-sm */}
            No Camera Feed Available
          </div>
        )}
        {locationName && (
          <div class="camera-feed-location-overlay"> {/* Replaced Tailwind: absolute bottom-0 left-0 bg-black bg-opacity-70 text-white text-sm px-3 py-1 rounded-tr-lg font-semibold */}
            {locationName}
          </div>
        )}
        {imageUrl && ( // Only show LIVE tag if an image is actually loaded
          <div class="camera-feed-live-tag"> {/* Replaced Tailwind: absolute top-2 right-2 bg-red-600 text-white text-xs px-2 py-1 rounded-full font-bold */}
            LIVE
          </div>
        )}
      </div>
      <p class="camera-feed-description">This feed updates periodically to simulate real-time visuals.</p> {/* Replaced Tailwind: text-sm text-gray-600 mt-4 text-center */}
    </div>
  );
};

export default CameraFeed;
