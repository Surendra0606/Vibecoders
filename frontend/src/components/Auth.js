// frontend/src/components/Auth.js
// This component handles user authentication (login/logout) and conditionally
// renders the main application content only if a user is authenticated.

import React, { useState, useEffect } from 'react';
import { auth } from '../firebaseConfig'; // Import the Firebase Auth instance
import { signInWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';

// Import the LoginPage component to use its styled UI for login
import LoginPage from './LoginPage'; // Make sure LoginPage.js is in the same 'components' folder

const Auth = ({ children }) => {
  const [user, setUser] = useState(null); // State to hold the currently logged-in user object
  const [loading, setLoading] = useState(true); // State to indicate if the authentication state is being loaded

  useEffect(() => {
    // onAuthStateChanged is a Firebase listener that triggers whenever the user's sign-in state changes.
    // It's crucial for managing persistent login sessions.
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser); // Set the user state to the current user (or null if logged out)
      setLoading(false); // Authentication state has been determined, so stop loading
    });
    return () => unsubscribe(); // Clean up the listener when the component unmounts
  }, []); // Empty dependency array means this effect runs only once on mount

  // Function to handle user login
  const handleLogin = async (email, password) => {
    try {
      setLoading(true); // Set loading true during login attempt
      await signInWithEmailAndPassword(auth, email, password); // Firebase login call
      console.log("Logged in successfully!");
    } catch (error) {
      console.error("Login error:", error.message);
      // For a hackathon, a simple alert is used. In a production app, use a custom modal or toast.
      alert("Login Failed: " + error.message);
    } finally {
      setLoading(false); // Set loading false after login attempt (success or failure)
    }
  };

  // Function to handle user logout
  const handleLogout = async () => {
    try {
      await signOut(auth); // Firebase logout call
      console.log("Logged out successfully!");
    } catch (error) {
      console.error("Logout error:", error.message);
      alert("Logout Failed: " + error.message);
    }
  };

  // Display a loading message while authentication state is being determined
  if (loading) {
    return (
      <div class="auth-loading-screen"> {/* Replaced Tailwind classes */}
        <p class="auth-loading-text">Loading authentication...</p> {/* Replaced Tailwind classes */}
      </div>
    );
  }

  // If no user is logged in, display the LoginPage component
  if (!user) {
    // Pass the handleLogin function as a prop to LoginPage
    return <LoginPage onLogin={handleLogin} />;
  }

  // If a user is logged in, render the children components (which will be your main App content)
  // Also provide a logout button.
  return (
    <>
      <button
        onClick={handleLogout}
        class="auth-logout-button" /* Replaced Tailwind classes */
      >
        Logout
      </button>
      {children}
    </>
  );
};

export default Auth;
