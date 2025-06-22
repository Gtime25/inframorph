import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, user, isAuthenticated }) => {
  // Check if user is authenticated (either by user object or isAuthenticated flag)
  const authenticated = user || isAuthenticated;
  
  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute; 