// frontend/src/components/CityInsightsPanel.js
// This component displays AI-generated city insights and recommendations
// fetched in real-time from the 'city_insights' Firestore collection.

import React, { useState, useEffect } from 'react';
import { collection, onSnapshot, query, orderBy, limit } from "firebase/firestore";
import { db } from '../firebaseConfig'; // Import the Firestore database instance

const CityInsightsPanel = () => {
  const [insights, setInsights] = useState([]); // State to store the list of insights
  const [loadingInsights, setLoadingInsights] = useState(true); // Loading state

  useEffect(() => {
    // Create a Firestore query: target 'city_insights' collection,
    // order by timestamp (descending to show most recent first), limit to 3 latest insights.
    const q = query(collection(db, "city_insights"), orderBy("timestamp", "desc"), limit(3));
    
    // onSnapshot sets up a real-time listener.
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const newInsights = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setInsights(newInsights);
      setLoadingInsights(false); // Insights loaded
    }, (error) => {
      console.error("Error fetching city insights:", error);
      setLoadingInsights(false); // Stop loading even on error
    });

    return () => unsubscribe(); // Cleanup the listener when the component unmounts
  }, []); // Empty dependency array means this effect runs only once on component mount

  return (
    <div className="insights-panel-container " style={{height:"300px", overflowY: 'scroll'}}> {/* Custom class for styling */}
      <h3 className="insights-panel-header">AI-Powered City Insights</h3> {/* Custom class for styling */}
      {loadingInsights ? (
        <p className="insights-loading-message">Loading insights...</p>
      ) : insights.length === 0 ? (
        <p className="insights-no-data-message">No recent insights generated yet. Please wait for the AI agent to process data.</p>
      ) : (
        <div className="insights-list custom-scrollbar"> {/* Custom class for styling, with scrollbar */}
          {insights.map(insight => (
            <div key={insight.id} className="insight-card"> {/* Custom class for individual insight cards */}
              <p className="insight-card-summary">{insight.insight_summary}</p> {/* Display the generated text */}
              <p className="insight-card-timestamp">
                Generated: {insight.timestamp ? new Date(insight.timestamp.seconds * 1000).toLocaleString() : 'N/A'}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CityInsightsPanel;