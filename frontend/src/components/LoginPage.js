// frontend/src/components/LoginPage.js
// This component provides a standalone login page UI using React and general CSS.
// It's designed to be clean, modern, and responsive, fitting the project's aesthetic.

import React from 'react';

// Accept 'onLogin' prop from the parent component (Auth.js)
const LoginPage = ({ onLogin }) => { 
  // This handleLogin will now call the onLogin prop received from Auth.js
  const handleLogin = (e) => {
    e.preventDefault(); // Prevent default form submission to handle login with Firebase
    const email = e.target.email.value;
    const password = e.target.password.value;
    // Call the onLogin prop, which is the actual Firebase login function from Auth.js
    onLogin(email, password); 
  };

  return (
    <div class="login-page-container"> {/* Replaced Tailwind classes */}
      <div class="login-card"> {/* Replaced Tailwind classes */}
        <h2 class="login-title">Welcome Back!</h2> {/* Replaced Tailwind classes */}
        <p class="login-subtitle">Sign in to access the Bengaluru City Monitor.</p> {/* Replaced Tailwind classes */}

        <form onSubmit={handleLogin}>
          <div class="form-group"> {/* Replaced Tailwind classes */}
            <label htmlFor="email" class="form-label"> {/* Replaced Tailwind classes */}
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="your.email@example.com"
              class="form-input" /* Replaced Tailwind classes */
              required
            />
          </div>

          <div class="form-group form-group-password"> {/* Replaced Tailwind classes */}
            <label htmlFor="password" class="form-label"> {/* Replaced Tailwind classes */}
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="••••••••"
              class="form-input" /* Replaced Tailwind classes */
              required
            />
          </div>

          <div class="flex-container-center-between"> {/* Custom class for flex layout */}
            <button
              type="submit"
              class="login-button" /* Replaced Tailwind classes */
            >
              Sign In
            </button>
          </div>

          <p class="signup-text"> {/* Replaced Tailwind classes */}
            Don't have an account? <button type="button" class="signup-button">Sign Up</button> {/* Replaced Tailwind <a> */}
          </p>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
