// AuthWrapper.js
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const AuthWrapper = ({ children }) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  const location = useLocation();

  if (!isAuthenticated && location.pathname !== '/login') {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default AuthWrapper;
