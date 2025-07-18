import { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import AddTeacher from './pages/AddTeacher';
import Teachers from './pages/Teachers';
import AddStudent from './pages/AddStudent';
const AppRoutes = () => {
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
                    isAuthenticated ? (
                        <Dashboard onLogout={() => setIsAuthenticated(false)} />
                    ) : (
                        <Navigate to="/" replace />
                    )
                }
            />
            <Route
                path="/students"
                element={
                    isAuthenticated ? <Students /> : <Navigate to="/" replace />
                } />
            <Route
                path="/teachers"
                element={
                    isAuthenticated ? <Teachers /> : <Navigate to="/" replace />
                } />
            <Route
                path="/add-teacher"
                element={
                    isAuthenticated ? <AddTeacher /> : <Navigate to="/" replace />
                } />
            <Route
                path="/add-student"
                element={
                    isAuthenticated ? <AddStudent /> : <Navigate to="/" replace />
                } />
        </Routes>
    )
}

export default AppRoutes;