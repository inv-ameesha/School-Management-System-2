import React, { useState } from 'react';
import { Container, TextField, Button, Typography, Alert, Box, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom'
const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/people/password-reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(data.message || 'If this email exists, a password reset link has been sent.');
      } else {
        setError(data.error || data.detail || 'Failed to send reset email.');
      }
    } catch (err) {
      setError('Failed to send reset email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ p: 4, mt: 8 }}>
        <Typography variant="h5" align="center" gutterBottom>
          Forgot Password
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Email"
            type="email"
            fullWidth
            margin="normal"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          {message && <Alert severity="success" sx={{ my: 2 }}>{message}</Alert>}
          {error && <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>}
          <Box textAlign="center" mt={2}>
            <Button type="submit" variant="contained" color="primary" disabled={loading}>
              {loading ? 'Sending...' : 'Send Reset Link'}
            </Button>
          </Box>
        </form>
      </Paper>
      <Button variant="outlined" sx={{ ml: 2,mt: 2 }} onClick={() => navigate('/')}>
        Login
      </Button>
    </Container>
  );
};

export default ForgotPassword;
