// ProtectedRoute.js
import React, { useState } from 'react';
import NProgress from 'nprogress';
import AdminSettings from './AdminSettings';
import getApiBaseUrl from './apiConfig';
import secureApi from './SecureApi';
const ProtectedRoute = () => {
  const [inputPassword, setInputPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    NProgress.start();
    setError('');

    try {
      const response = await secureApi.post(`${getApiBaseUrl()}/login`, {
        password: inputPassword
      });

      if (response.data.message === "Login successful") {
        setIsAuthenticated(true);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'An error occurred during authentication';
      setError(errorMessage);
      console.error('Error during authentication:', error);
    } finally {
      NProgress.done();
    }
  };

  if (isAuthenticated) {
    return <AdminSettings />;
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
