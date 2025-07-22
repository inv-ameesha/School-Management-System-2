import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Button, Paper, TextField, IconButton, Alert } from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';
import { useNavigate } from 'react-router-dom';

const initialQuestion = { text: '', options: ['', '', '', ''], correct_option: 0 };

const TeacherExams = () => {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState('');
  const [questions, setQuestions] = useState([ { ...initialQuestion } ]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [exams, setExams] = useState([]);
  const [loadingExams, setLoadingExams] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    // Fetch exams created by this teacher
    const fetchExams = async () => {
      setLoadingExams(true);
      setExams([]);
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:8000/people/exams/created-by-me/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setExams(data);
        }
      } catch (err) {

      } finally {
        setLoadingExams(false);
      }
    };
    fetchExams();
  }, [message]); // refetch after creating an exam

  const handleQuestionChange = (idx, field, value) => {
    const updated = [...questions];
    if (field === 'text') updated[idx].text = value;
    else if (field === 'correct_option') updated[idx].correct_option = parseInt(value);
    setQuestions(updated);
  };

  const handleOptionChange = (qIdx, optIdx, value) => {
    const updated = [...questions];
    updated[qIdx].options[optIdx] = value;
    setQuestions(updated);
  };

  const addQuestion = () =>
    setQuestions([
      ...questions,
      { text: '', options: ['', '', '', ''], correct_option: 0 }
    ]);
  const removeQuestion = (idx) => setQuestions(questions.length > 1 ? questions.filter((_, i) => i !== idx) : questions);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8000/people/exams/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title,
          description,
          duration,
          subject: 'Science', 
          date: '2025-07-22', 
          questions: questions.map(q => ({
            text: q.text,
            option_a: q.options[0],
            option_b: q.options[1],
            option_c: q.options[2],
            option_d: q.options[3],
            correct_option: ['a', 'b', 'c', 'd'][q.correct_option],
          })),
        }),
      });
      if (res.ok) {
        setMessage('Exam created successfully!');
        setShowForm(false);
        setTitle('');
        setDescription('');
        setDuration('');
        setQuestions([{ ...initialQuestion }]);
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to create exam.');
      }
    } catch (err) {
      setError('Failed to create exam.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          Manage Exams
        </Typography>
        <Box mt={3}>
          <Button variant="contained" color="primary" sx={{ mr: 2 }} onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'Create New Exam'}
          </Button>
          <Button variant="outlined" color="secondary" onClick={() => navigate('/assign-exam')}>
            Assign Exam to Students
          </Button>
        </Box>
        {showForm && (
          <Box component="form" onSubmit={handleSubmit} mt={4}>
            <TextField
              label="Exam Title"
              fullWidth
              margin="normal"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
            />
            <TextField
              label="Description"
              fullWidth
              margin="normal"
              value={description}
              onChange={e => setDescription(e.target.value)}
              required
            />
            <TextField
              label="Duration (minutes)"
              type="number"
              fullWidth
              margin="normal"
              value={duration}
              onChange={e => setDuration(e.target.value)}
              required
            />
            <Typography variant="h6" mt={3}>Questions</Typography>
            {questions.map((q, idx) => (
              <Paper key={idx} sx={{ p: 2, mt: 2, mb: 2 }}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="subtitle1">Question {idx + 1}</Typography>
                  <IconButton onClick={() => removeQuestion(idx)} disabled={questions.length === 1}>
                    <RemoveCircleOutlineIcon />
                  </IconButton>
                </Box>
                <TextField
                  label="Question Text"
                  fullWidth
                  margin="normal"
                  value={q.text}
                  onChange={e => handleQuestionChange(idx, 'text', e.target.value)}
                  required
                />
                {q.options.map((opt, oIdx) => (
                  <TextField
                    key={oIdx}
                    label={`Option ${oIdx + 1}`}
                    fullWidth
                    margin="normal"
                    value={opt}
                    onChange={e => handleOptionChange(idx, oIdx, e.target.value)}
                    required
                  />
                ))}
                <TextField
                  select
                  label="Correct Option"
                  fullWidth
                  margin="normal"
                  SelectProps={{ native: true }}
                  value={q.correct_option}
                  onChange={e => handleQuestionChange(idx, 'correct_option', e.target.value)}
                  required
                >
                  {[0, 1, 2, 3].map(i => (
                    <option key={i} value={i}>{`Option ${i + 1}`}</option>
                  ))}
                </TextField>
              </Paper>
            ))}
            <Button startIcon={<AddCircleOutlineIcon />} onClick={addQuestion} sx={{ mt: 2 }}>
              Add Question
            </Button>
            {message && <Alert severity="success" sx={{ mt: 2 }}>{message}</Alert>}
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            <Box textAlign="center" mt={3}>
              <Button type="submit" variant="contained" color="primary" disabled={loading}>
                {loading ? 'Creating...' : 'Create Exam'}
              </Button>
            </Box>
          </Box>
        )}
        <Box mt={5}>
          <Typography variant="h6">Your Exams</Typography>
          {loadingExams ? (
            <Typography>Loading...</Typography>
          ) : exams.length === 0 ? (
            <Typography color="text.secondary">No exams found.</Typography>
          ) : (
            <Box mt={2}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ borderBottom: '1px solid #ccc' }}>SI.no</th>
                    <th style={{ borderBottom: '1px solid #ccc' }}>Exam Name</th>
                  </tr>
                </thead>
                <tbody>
                  {exams.map((exam, idx) => (
                    <tr key={exam.id || idx}>
                      <td style={{ textAlign: 'center' }}>{idx + 1}</td>
                      <td>{exam.title}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
          )}
        </Box>
      </Paper>
      <Button variant="outlined" sx={{ ml: 2,mt: 2 }} onClick={() => navigate('/dashboard')}>
        Back
      </Button>
    </Container>
  );
};

export default TeacherExams; 