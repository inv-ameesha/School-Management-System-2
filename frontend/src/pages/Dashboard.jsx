import '../App.css';
import { Box, Button, Container, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

const Dashboard = ({ onLogout }) => {
  const navigate = useNavigate();
  const role = localStorage.getItem('role');
  const handleLogout = () => {
    onLogout();
    navigate('/');
  };
  const [studentDetails, setStudentDetails] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (role === 'student' && showDetails && !studentDetails) {
      // Fetch student details from backend
      const token = localStorage.getItem('token');
      fetch('http://localhost:8000/people/students/me/', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => setStudentDetails(data));
    }
  }, [role, showDetails, studentDetails]);
  return (
    <Container>
      <Box textAlign="center" mt={4}>
        <Typography variant='h4' gutterBottom>
          {role === 'admin' ? 'Admin' : role === 'teacher' ? 'Teacher' : 'Student'} Dashboard
        </Typography>
      </Box>

      {role === 'student' ? (
        <Box textAlign="center" mt={4}>
          <Typography variant="h6">Welcome to your student dashboard!</Typography>
          <Button variant="contained" sx={{ m: 1 }} onClick={() => { setShowDetails(true); }}>
            View Details
          </Button>
          <Button variant="contained" sx={{ m: 1 }} onClick={() => navigate('/student-exams')}>
            View Exams
          </Button>
          {showDetails && studentDetails && (
            <Box mt={3} textAlign="left">
              <Typography variant="subtitle1">Your Details:</Typography>
              <ol>
                {Object.entries(studentDetails)
                  .filter(([key]) => key !== 'id' && key !== 'user') 
                  .map(([key, value]) => (
                    <li key={key}>
                      <strong>{key.replace(/_/g, ' ')}:</strong> {String(value)}
                    </li>
                  ))}
              </ol>

            </Box>
          )}
          <Button variant="contained" color="primary" onClick={handleLogout} sx={{ mt: 3 }}>
            Logout
          </Button>
        </Box>
      ) : (
        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: 2,
            mt: 4,
          }}
        >
          <Button variant="contained" onClick={() => navigate('/students')}>
            View Students
          </Button>

          {role === 'admin' && (
            <Button variant="contained" onClick={() => navigate('/teachers')}>
              View Teachers
            </Button>
          )}

          <Button variant="contained" onClick={() => navigate('/add-student')}>
            Add Students
          </Button>

          {role === 'admin' && (
            <Button variant="contained" onClick={() => navigate('/add-teacher')}>
              Add Teachers
            </Button>
          )}

          {role === 'teacher' && (
            <Button variant="contained" color="secondary" onClick={() => navigate('/teacher-exams')}>
              Manage Exams
            </Button>
          )}

          <button onClick={handleLogout}>Logout</button>
        </Box>
      )}
    </Container>
  );
};

export default Dashboard;
