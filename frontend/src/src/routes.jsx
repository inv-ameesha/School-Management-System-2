import { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import AddTeacher from './pages/AddTeacher';
import Teachers from './pages/Teachers';
import AddStudent from './pages/AddStudent';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import TeacherExams from './pages/TeacherExams';
import AssignExam from './pages/AssignExam';
import StudentExams from './pages/StudentExams';
import AttemptExam from './pages/AttemptExam';
import StudentDetails from './pages/StudentDetails';
import EditStudent from './pages/EditStudent';
import EditTeacher from './pages/EditTeacher';
import Layout from './pages/Layout';
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
            <Route element={<Layout />}>
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
                <Route
                    path="/forgot-password"
                    element={<ForgotPassword />}
                />
                <Route
                    path="/reset-password-confirm/:uidb64/:token"
                    element={<ResetPassword />}
                />
                <Route
                    path="/teacher-exams"
                    element={<TeacherExams />}
                />
                <Route
                    path="/assign-exam"
                    element={<AssignExam />}
                />
                <Route
                    path="/student-exams"
                    element={<StudentExams />}
                />
                <Route path="/attempt-exam/:examId" element={<AttemptExam />} />
                <Route path="/student-details" element={<StudentDetails />} />
                <Route path="/edit-student/:id" element={<EditStudent />} />
                <Route path="/edit-teacher/:id" element={<EditTeacher />} />
            </Route>
        </Routes>
    )
}

export default AppRoutes;