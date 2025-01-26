// ProtectedRoute.js
import React, { useState } from 'react';
import NProgress from 'nprogress';
import AdminSettings from './AdminSettings';
import getApiBaseUrl from './apiConfig';
const ProtectedRoute = () => {
  const [inputPassword, setInputPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    NProgress.start();

    try {
      const response = await fetch(`${getApiBaseUrl()}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: inputPassword }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data.message);
        setIsAuthenticated(true);
      } else {
        alert('Incorrect password. Please try again.');
      }
    } catch (error) {
      console.error('Error during authentication:', error);
    } finally {
      NProgress.done();
    }
  };

  if (isAuthenticated) {
    return (
      <div>
        <AdminSettings />
      </div>
    );
  }

  return (
    <div className="protected-route">
      <h2>Password Protected Route</h2>
      <form onSubmit={handlePasswordSubmit}>
        <input
          type="password"
          placeholder="Enter password"
          value={inputPassword}
          onChange={(e) => setInputPassword(e.target.value)}
        />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default ProtectedRoute;
