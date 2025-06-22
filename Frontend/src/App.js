import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Analysis from './pages/Analysis';
import Results from './pages/Results';
import GitHubConnect from './pages/GitHubConnect';
import DriftDetection from './pages/DriftDetection';
import SecurityAnalysis from './pages/SecurityAnalysis';
import ProtectedRoute from './components/ProtectedRoute';
import Onboarding from './components/Onboarding';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    // Check for existing session
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    
    setLoading(false);
  }, []);

  const handleLogin = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
    localStorage.setItem('token', userToken);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const handleShowOnboarding = () => {
    setShowOnboarding(true);
  };

  const handleCloseOnboarding = () => {
    setShowOnboarding(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading InfraMorph...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Toaster position="top-right" />
        
        {showOnboarding && (
          <Onboarding onClose={handleCloseOnboarding} />
        )}
        
        <Header 
          user={user} 
          onLogout={handleLogout} 
          onShowOnboarding={handleShowOnboarding}
        />
        
        <Routes>
          <Route 
            path="/" 
            element={
              user ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
            } 
          />
          
          <Route 
            path="/login" 
            element={
              user ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />
            } 
          />
          
          <Route 
            path="/signup" 
            element={
              user ? <Navigate to="/dashboard" /> : <Signup onLogin={handleLogin} />
            } 
          />
          
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute user={user}>
                <Dashboard user={user} token={token} />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/analysis" 
            element={
              <ProtectedRoute user={user}>
                <Analysis user={user} token={token} />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/analysis/:analysisId" 
            element={
              <ProtectedRoute user={user}>
                <Results user={user} token={token} />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/results/:analysisId" 
            element={
              <ProtectedRoute user={user}>
                <Results user={user} token={token} />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/github-connect" 
            element={
              <ProtectedRoute user={user}>
                <GitHubConnect user={user} token={token} />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/drift-detection" 
            element={
              <ProtectedRoute user={user}>
                <DriftDetection user={user} token={token} />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/security-analysis" 
            element={
              <ProtectedRoute user={user}>
                <SecurityAnalysis user={user} token={token} />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 