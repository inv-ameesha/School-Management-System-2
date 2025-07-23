import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Button, Paper, List, ListItem, ListItemText, ListItemSecondaryAction, CircularProgress, Alert, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const StudentExams = () => {
  const [assignments, setAssignments] = useState([]);
  const [examDetails, setExamDetails] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedExamId, setSelectedExamId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAssignedExams = async () => {
      setLoading(true);
      setError('');
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/'); 
          return;
        }
        const res = await fetch('http://localhost:8000/people/exams/assigned/', {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        if (res.ok) {
          const data = await res.json();
          setAssignments(data);
          const examIds = data.map(a => a.exam);
          const details = {};
          await Promise.all(
            examIds.map(async (id) => {
              try {
                const examRes = await fetch(`http://localhost:8000/people/exams/${id}/`, {
                  headers: { Authorization: `Bearer ${token}` },
                });
                if (examRes.ok) {
                  const examData = await examRes.json();
                  details[id] = examData;
                }
              } catch { }
            })
          );
          setExamDetails(details);
        } else {
          setError('Failed to fetch assigned exams.');
        }
      } catch (err) {
        setError('Failed to fetch assigned exams.');
      } finally {
        setLoading(false);
      }
    };
    fetchAssignedExams();
  }, []);

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          My Assigned Exams
        </Typography>
        {loading ? (
          <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
        ) : assignments.length === 0 ? (
          <Alert severity="info" sx={{ mt: 2 }}>No exams assigned yet.</Alert>
        ) : (
          <List>
            {assignments.map((assignment) => {
              const exam = examDetails[assignment.exam];
              return (
                <ListItem key={assignment.id} divider>
                  <ListItemText
                    primary={exam ? exam.title : `Exam #${assignment.exam}`}
                    secondary={exam ? exam.description : ''}
                  />
                  <ListItemSecondaryAction>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={() => {
                        setSelectedExamId(assignment.exam);
                        setOpenDialog(true);
                      }}
                      disabled={assignment.alreadyAttempted}
                    >
                      Attempt
                    </Button>
                  </ListItemSecondaryAction>
                </ListItem>
              );
            })}
          </List>
        )}
        <Box textAlign="center" mt={3}>
          <Button variant="outlined" onClick={() => navigate(-1)}>
            Back
          </Button>
        </Box>
      </Paper>
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Start Exam</DialogTitle>
        <DialogContent>
          Are you sure you want to start the exam now?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} color="error">
            No
          </Button>
          <Button
            onClick={() => {
              setOpenDialog(false);
              navigate(`/attempt-exam/${selectedExamId}`);
            }}
            color="primary"
            autoFocus
          >
            Yes
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default StudentExams; 