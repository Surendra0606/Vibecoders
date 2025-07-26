// // frontend/src/App.js
// // This is the main application component. It sets up the overall layout,
// // integrates authentication, and includes the various dashboard panels.

// import React, { useRef, useState, useEffect } from 'react'; // Import useRef, useState, useEffect
// import './index.css'; // Import global CSS (now contains all styling)
// import Auth from './components/Auth'; // Component for handling user authentication
// import MapComponent from './components/MapComponent'; // Component for displaying the interactive map
// import AlertsPanel from './components/AlertsPanel'; // Component for displaying live alerts
// import CameraFeed from './components/CameraFeed'; // Component for displaying the simulated camera feed

// function App() {
//   const mapWrapperRef = useRef(null); // Create a ref to attach to the map wrapper div
//   const [mapContainerHeight, setMapContainerHeight] = useState(0); // State to store the measured height

//   // useEffect to measure the height of the map wrapper div after render
//   useEffect(() => {
//     const measureHeight = () => {
//       if (mapWrapperRef.current) {
//         const height = mapWrapperRef.current.clientHeight;
//         setMapContainerHeight(height);
//         console.log("Map Container Height:", height); // Log the measured height
//       }
//     };

//     // Measure height initially
//     measureHeight();

//     // Add event listener for window resize to re-measure height
//     window.addEventListener('resize', measureHeight);

//     // Cleanup function to remove the event listener
//     return () => {
//       window.removeEventListener('resize', measureHeight);
//     };
//   }, []); // Empty dependency array means this effect runs once on mount

//   return (
//     // The Auth component wraps the entire application. It will show a login screen
//     // if the user is not authenticated, and the dashboard content if they are.
//     <Auth>
//       <div className="app-container">
//         {/* Header Section */}
//         <header className="app-header">
//           Bengaluru City Monitor - Agentic AI Day
//         </header>

//         {/* Main Content Area: Flex container for map and side panels */}
//         <main className="app-main-content">
//           {/* Left Column: Map & Sentiment/Crowd Insights */}
//           <div className="app-left-column">
//             {/* Live City Map Panel */}
//             <div className="app-panel app-panel-map">
//                 <h2 class="app-panel-header app-panel-header-blue">Live City Map & Insights</h2>
//                 {/* Attach the ref to this div and pass its measured height to MapComponent */}
//                 {/* TEMPORARY: Added inline style for visual debugging of the wrapper's height */}
//                 <div 
//                   className="map-component-wrapper" 
//                   ref={mapWrapperRef} 
//                   style={{ backgroundColor: mapContainerHeight === 0 ? 'pink' : 'lightgreen', border: '2px dashed purple' }} // Visual debug
//                 >
//                     {/* Pass the measured height to MapComponent */}
//                     <MapComponent containerHeight={mapContainerHeight} /> 
//                 </div>
                
//                 {/* Sentiment & Crowd Key (Visual Guide) */}
//                 <div class="map-key-grid">
//                     <div class="map-key-item map-key-item-green">
//                         <span class="map-key-dot map-key-dot-green"></span>
//                         <span class="map-key-text">Positive Sentiment / Low Density</span>
//                     </div>
//                     <div class="map-key-item map-key-item-yellow">
//                         <span class="map-key-dot map-key-dot-yellow"></span>
//                         <span class="map-key-text">Neutral Sentiment / Medium Density</span>
//                         </div>
//                     <div class="map-key-item map-key-item-red">
//                         <span class="map-key-dot map-key-dot-red"></span>
//                         <span class="map-key-text">Negative Sentiment / High Density</span>
//                     </div>
//                 </div>
//             </div>
//           </div>

//           {/* Right Column: Alerts & Camera Feed */}
//           <div className="app-right-column">
//             {/* Live Alerts Panel */}
//             <div className="app-panel app-panel-alerts">
//                 <h3 class="app-panel-header app-panel-header-red">Live Alerts</h3>
//                 <div class="space-y-4 custom-scrollbar overflow-y-auto flex-1">
//                     <AlertsPanel />
//                 </div>
//             </div>

//             {/* Simulated Camera Feed Panel */}
//             <div class="app-panel app-panel-camera">
//                 <h3 class="app-panel-header app-panel-header-green">Simulated Camera Feed</h3>
//                 <CameraFeed />
//             </div>
//           </div>
//         </main>

//         {/* Footer Section */}
//         <footer class="app-footer">
//             &copy; 2025 VibeCoders007 - Agentic AI Day. All rights reserved.
//         </footer>
//       </div>
//     </Auth>
//   );
// }

// export default App;


// frontend/src/App.js
// This is the main application component. It sets up the overall layout,
// integrates authentication, and includes the various dashboard panels.

import React, { useRef, useState, useEffect } from 'react'; // Import useRef, useState, useEffect
import './index.css'; // Import global CSS (now contains all styling)
import Auth from './components/Auth'; // Component for handling user authentication
import MapComponent from './components/MapComponent'; // Component for displaying the interactive map
import AlertsPanel from './components/AlertsPanel'; // Component for displaying live alerts
import CityInsightsPanel from './components/CityInsightsPanel'; // Import the new CityInsightsPanel

function App() {
  const mapWrapperRef = useRef(null); // Create a ref to attach to the map wrapper div
  const [mapContainerHeight, setMapContainerHeight] = useState(0); // State to store the measured height

  // useEffect to measure the height of the map wrapper div after render
  useEffect(() => {
    const measureHeight = () => {
      if (mapWrapperRef.current) {
        const height = mapWrapperRef.current.clientHeight;
        setMapContainerHeight(height);
        console.log("Map Container Height:", height); // Log the measured height
      }
    };

    // Measure height initially
    measureHeight();

    // Add event listener for window resize to re-measure height
    window.addEventListener('resize', measureHeight);

    // Cleanup function to remove the event listener
    return () => {
      window.removeEventListener('resize', measureHeight);
    };
  }, []); // Empty dependency array means this effect runs once on mount

  return (
    // The Auth component wraps the entire application. It will show a login screen
    // if the user is not authenticated, and the dashboard content if they are.
    <Auth>
      <div className="app-container">
        {/* Header Section */}
        <header className="app-header">
          Bengaluru City Crowd Data Analytics 
        </header>

        {/* Main Content Area: Flex container for map and side panels */}
        <main className="app-main-content">
          {/* Left Column: Map & Sentiment/Crowd Insights */}
          <div className="app-left-column">
            {/* Live City Map Panel */}
            <div className="app-panel app-panel-map">
                <h2 class="app-panel-header app-panel-header-blue">Live City Map & Insights</h2>
                {/* Attach the ref to this div. The height is now applied directly to map-component-wrapper */}
                <div 
                  className="map-component-wrapper" 
                  ref={mapWrapperRef} 
                  // Apply measured height directly as an inline style
                  style={{ height: mapContainerHeight > 0 ? mapContainerHeight : '400px' }} // Fallback to 400px if 0
                >
                    {/* MapComponent no longer needs containerHeight prop, it will inherit from its parent */}
                    <MapComponent /> 
                </div>
                
                {/* Sentiment & Crowd Key (Visual Guide) */}
                {/* <div class="map-key-grid">
                    <div class="map-key-item map-key-item-green">
                        <span class="map-key-dot map-key-dot-green"></span>
                        <span class="map-key-text">Positive Sentiment -😁 / Low Density - 🟢</span>
                    </div>
                    <div class="map-key-item map-key-item-yellow">
                        <span class="map-key-dot map-key-dot-yellow"></span>
                        <span class="map-key-text">Neutral Sentiment - 🙂 / Medium Density - 🟠</span>
                        </div>
                    <div class="map-key-item map-key-item-red">
                        <span class="map-key-dot map-key-dot-red"></span>
                        <span class="map-key-text">Negative Sentiment - 😢/ High Density - 🔴</span>
                    </div>
                </div> */}
            </div>
          </div>

          {/* Right Column: Alerts & City Insights */}
          <div className="app-right-column">
            {/* Live Alerts Panel */}
            <div className="app-panel app-panel-alerts">
                <h3 class="app-panel-header app-panel-header-red">Live Alerts</h3>
                <div class="alerts-list-container custom-scrollbar">
                    <AlertsPanel />
                </div>
            </div>

            {/* AI-Powered City Insights Panel (New Section) */}
            <div class="app-panel app-panel-insights">
                <h3 class="app-panel-header app-panel-header-purple">AI City Insights</h3>
                <CityInsightsPanel /> {/* Render the new insights component */}
            </div>
          </div>
        </main>

        {/* Footer Section */}
        <footer class="app-footer">
            &copy; 2025 VibeCoders007 - Agentic AI Day. All rights reserved.
        </footer>
      </div>
    </Auth>
  );
}

export default App;
