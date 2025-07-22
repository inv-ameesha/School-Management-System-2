import React, { useEffect, useState } from 'react';
import { Container, Typography, Paper, Box, CircularProgress, Alert, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const StudentDetails = () => {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDetails = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/');
        return;
      }
      try {
        const res = await fetch('http://localhost:8000/people/students/me/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setDetails(data);
        } else {
          setError('Failed to fetch student details.');
        }
      } catch {
        setError('Failed to fetch student details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [navigate]);

  if (loading) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>;
  if (!details) return null;

  // Fields to hide
  const hiddenFields = ['id', 'user', 'assigned_teacher'];

  return (
    <Container maxWidth="sm" sx={{ mt: 6 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          Student Details
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 3 }}>
          {Object.entries(details)
            .filter(([key]) => !hiddenFields.includes(key))
            .map(([key, value]) => (
              <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: '#f5f5f5', borderRadius: 2, p: 2, boxShadow: 1 }}>
                <Typography sx={{ fontWeight: 600, textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}:</Typography>
                <Typography>{String(value)}</Typography>
              </Box>
            ))}
        </Box>
        <Box textAlign="center" mt={3}>
          <Button variant="outlined" onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default StudentDetails; 