import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Box, Button, Paper, Radio, RadioGroup, FormControlLabel, CircularProgress, Alert, Dialog, DialogTitle, DialogContent } from '@mui/material';

const AttemptExam = () => {
  const { examId } = useParams();
  const [exam, setExam] = useState(null);
  const [answers, setAnswers] = useState({});
  const [timer, setTimer] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openThankYou, setOpenThankYou] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchExam = async () => {
      setLoading(true);
      setError('');
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`http://localhost:8000/people/exams/${examId}/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setExam(data);
          setTimer(data.duration * 60); 
        } else {
          setError('Failed to fetch exam details.');
        }
      } catch (err) {
        setError('Failed to fetch exam details.');
      } finally {
        setLoading(false);
      }
    };
    fetchExam();
  }, [examId]);

  // Timer logic
  useEffect(() => {
    if (timer <= 0) return;
    const interval = setInterval(() => setTimer(t => t - 1), 1000);
    return () => clearInterval(interval);
  }, [timer]);

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleSubmit = async () => {
    const token = localStorage.getItem('token');
    await fetch(`http://localhost:8000/people/exams/${examId}/attempt/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
      }),
    });
    setOpenThankYou(true);
    setTimeout(() => {
      setOpenThankYou(false);
      navigate('/student-exams');
    }, 3000);
  };

  if (loading) return <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>;
  if (!exam) return null;

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Time Left: {Math.floor(timer / 60)}:{String(timer % 60).padStart(2, '0')}
          </Typography>
          <Button variant="contained" color="primary" onClick={handleSubmit}>
            Submit
          </Button>
        </Box>
        <Typography variant="h4" gutterBottom align="center">
          {exam.title}
        </Typography>
        {exam.questions && exam.questions.length > 0 ? (
          exam.questions.map((q, idx) => (
            <Box key={q.id || idx} mt={3}>
              <Typography variant="subtitle1">{idx + 1}. {q.text}</Typography>
              <RadioGroup
                value={answers[q.id] || ''}
                onChange={e => handleAnswerChange(q.id, e.target.value)}
              >
                <FormControlLabel value="a" control={<Radio />} label={q.option_a} />
                <FormControlLabel value="b" control={<Radio />} label={q.option_b} />
                <FormControlLabel value="c" control={<Radio />} label={q.option_c} />
                <FormControlLabel value="d" control={<Radio />} label={q.option_d} />
              </RadioGroup>
            </Box>
          ))
        ) : (
          <Typography>No questions found for this exam.</Typography>
        )}
      </Paper>
      <Dialog open={openThankYou} onClose={() => {}} disableEscapeKeyDown>
        <DialogTitle>Thank You!</DialogTitle>
        <DialogContent>
          Thank you for attempting the exam.<br />
          You will be redirected  shortly.
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default AttemptExam;