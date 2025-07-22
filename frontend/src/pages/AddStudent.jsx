import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from '../api/axios';
import {
  Container,
  TextField,
  Button,
  Typography,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Box,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { UploadFile } from '@mui/icons-material';
const AddStudent = () => {
  const { register, handleSubmit, reset } = useForm();
  const [teachers, setTeachers] = useState([]);
  const [message, setMessage] = useState('');
  const [importedStudents, setImportedStudents] = useState([]);
  const [importError, setImportError] = useState('');
  const navigate = useNavigate();
  const fileInputRef = React.useRef();
  useEffect(() => {
    const fetchTeachers = async () => {
      try {
        const res = await axios.get('/teachers/');
        setTeachers(res.data);
      } catch (err) {
        console.error('Error fetching teachers:', err);
      }
    };
    fetchTeachers();
  }, []);

  const onSubmit = async (data) => {
    try {
      await axios.post('/students/', data);
      setMessage('Student added successfully');
      reset();
    } catch (err) {
      console.error(err.response?.data || err.message);
      setMessage('Failed to add student');
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setMessage('');
    setImportError('');
    setImportedStudents([]);
    try {
      const res = await axios.post('/import/students/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage(res.data.message || 'Students imported successfully');
    } catch (err) {
      setImportError(err.response?.data?.error || 'Failed to import students');
    }
  };

  const handleFileButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 5, mb: 5 }}>
      <Typography variant="h4" gutterBottom align="center">
        Add Student
      </Typography>
      <Button
        variant="outlined"
        startIcon={<UploadFile />}
        onClick={handleFileButtonClick}
        sx={{ mb: 2 }}
      >
        Import Students (CSV)
      </Button>
      <input
        type="file"
        accept=".csv"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      {message && <Alert severity="success">{message}</Alert>}
      {importError && <Alert severity="error">{importError}</Alert>}

      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ mt: 3 }}>
        <TextField fullWidth label="First Name" margin="normal" {...register('first_name')} required />
        <TextField fullWidth label="Last Name" margin="normal" {...register('last_name')} required />
        <TextField fullWidth label="Phone Number" margin="normal" {...register('phone_number')} required />
        <TextField fullWidth label="Roll Number" margin="normal" {...register('roll_number')} required />
        <TextField fullWidth label="Class" margin="normal" {...register('student_class')} required />
        <TextField fullWidth type="date" margin="normal" {...register('date_of_birth')} required InputLabelProps={{ shrink: true }} label="Date of Birth" />
        <TextField fullWidth type="date" margin="normal" {...register('admission_date')} required InputLabelProps={{ shrink: true }} label="Admission Date" />

        <FormControl fullWidth margin="normal">
          <InputLabel>Status</InputLabel>
          <Select defaultValue="" label="Status" {...register('status')} required>
            <MenuItem value="Active">Active</MenuItem>
            <MenuItem value="Inactive">Inactive</MenuItem>
          </Select>
        </FormControl>

        <TextField fullWidth label="Username" margin="normal" {...register('username')} required />
        <TextField fullWidth label="Password" type="password" margin="normal" {...register('password')} required />
        <TextField fullWidth label="Email" type="email" margin="normal" {...register('email')} required />

        <TextField
          fullWidth
          label="Assigned Teacher"
          margin="normal"
          {...register('assigned_teacher')}
          required
        />

        <Button fullWidth type="submit" variant="contained" sx={{ mt: 3 }}>
          Add Student
        </Button>
      </Box>
      <Button variant="outlined" sx={{ ml: 2,mt: 2 }} onClick={() => navigate('/dashboard')}>
        Back
      </Button>
    </Container>
  );
};

export default AddStudent;
