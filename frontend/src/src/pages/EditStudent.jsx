import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, TextField, Button, Paper, Box, Alert, CircularProgress } from '@mui/material';

const EditStudent = () => {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStudent = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`http://localhost:8000/people/students/${id}/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setStudent(data);
        } else {
          setError('Failed to fetch student details.');
        }
      } catch {
        setError('Failed to fetch student details.');
      } finally {
        setLoading(false);
      }
    };
    fetchStudent();
  }, [id]);

  const handleChange = (e) => {
    setStudent({ ...student, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`http://localhost:8000/people/students/${id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(student),
      });
      if (res.ok) {
        setSuccess('Student updated successfully!');
      } else {
        setError('Failed to update student.');
      }
    } catch {
      setError('Failed to update student.');
    }
  };

  if (loading) return <Box display="flex" justifyContent="center" mt={6}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>;
  if (!student) return null;

  return (
    <Container maxWidth="sm" sx={{ mt: 6 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          Edit Student
        </Typography>
        <form onSubmit={handleSubmit}>
          {Object.entries(student).map(([key, value]) => (
            key !== 'id' && key !== 'user' && key !== 'assigned_teacher' && (
              <TextField
                key={key}
                name={key}
                label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                value={value || ''}
                onChange={handleChange}
                fullWidth
                margin="normal"
              />
            )
          ))}
          <Box textAlign="center" mt={3}>
            <Button type="submit" variant="contained" color="primary">Save</Button>
            <Button variant="outlined" sx={{ ml: 2 }} onClick={() => navigate('/students')}>Back</Button>
          </Box>
          {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        </form>
      </Paper>
    </Container>
  );
};

export default EditStudent; 