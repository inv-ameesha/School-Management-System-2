import { useState } from 'react';
import { Routes, Route,Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
const AppRoutes = () =>{
    const [isAuthenticated, setIsAuthenticated] = useState(false);
   return (
        <Routes>
                <Route
                path="/"
                element={
                    isAuthenticated ? (
                    <Navigate to="/dashboard" replace />
                    ) : (
                    <LoginPage onLogin={() => setIsAuthenticated(true)} />
                    )
                }
                />
                <Route
                path="/dashboard"
                element={
                    isAuthenticated ? <Dashboard /> : <Navigate to="/" replace />
                }
                />
                <Route 
                path="/students" 
                element={
                    isAuthenticated ? <Students /> : <Navigate to="/" replace />
                } />
        </Routes>
      )
}

export default AppRoutes;