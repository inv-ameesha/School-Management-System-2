import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Button, Paper, FormControl, InputLabel, Select, MenuItem, Checkbox, List, ListItem, ListItemText, ListItemSecondaryAction, CircularProgress, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const AssignExam = () => {
  const [exams, setExams] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedExam, setSelectedExam] = useState('');
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        const examsRes = await fetch('http://localhost:8000/people/exams/created-by-me/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const examsData = examsRes.ok ? await examsRes.json() : [];
        setExams(examsData);
        const studentsRes = await fetch('http://localhost:8000/people/students/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const studentsData = studentsRes.ok ? await studentsRes.json() : [];
        setStudents(studentsData);
      } catch (err) {
        setError('Failed to fetch data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleStudentToggle = (id) => {
    setSelectedStudents((prev) =>
      prev.includes(id) ? prev.filter((sid) => sid !== id) : [...prev, id]
    );
  };

  const handleAssign = async () => {
    setAssigning(true);
    setMessage('');
    setError('');
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8000/people/exams/assign/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          exam: selectedExam,
          students: selectedStudents,
        }),
      });
      if (res.ok) {
        setMessage('Exam assigned successfully!');
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to assign exam.');
      }
    } catch (err) {
      setError('Failed to assign exam.');
    } finally {
      setAssigning(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          Assign Exam to Students
        </Typography>
        {loading ? (
          <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>
        ) : (
          <>
            <FormControl fullWidth margin="normal" variant="outlined">
              <InputLabel id="exam-label">Select Exam</InputLabel>
              <Select
                labelId="exam-label"
                id="exam-select"
                value={selectedExam}
                onChange={(e) => setSelectedExam(e.target.value)}
                label="Select Exam"  
                required
              >
                {exams.map((exam) => (
                  <MenuItem key={exam.id} value={exam.id}>
                    {exam.title}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography variant="h6" mt={3}>Students</Typography>
            <List>
              {students.map((student) => (
                <ListItem key={student.id} button onClick={() => handleStudentToggle(student.id)}>
                  <ListItemText primary={`${student.first_name} ${student.last_name}`} secondary={student.email} />
                  <ListItemSecondaryAction>
                    <Checkbox
                      edge="end"
                      onChange={() => handleStudentToggle(student.id)}
                      checked={selectedStudents.includes(student.id)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
            {message && <Alert severity="success" sx={{ mt: 2 }}>{message}</Alert>}
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            <Box textAlign="center" mt={3}>
              <Button
                variant="contained"
                color="primary"
                disabled={assigning || !selectedExam || selectedStudents.length === 0}
                onClick={handleAssign}
              >
                {assigning ? 'Assigning...' : 'Assign to Selected'}
              </Button>
              <Button variant="outlined" sx={{ ml: 2 }} onClick={() => navigate('/dashboard')}>
                Back
              </Button>
            </Box>
          </>
        )}
      </Paper>
    </Container>
  );
};

export default AssignExam; 