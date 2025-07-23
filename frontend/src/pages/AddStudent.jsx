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
  FormHelperText,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { UploadFile } from '@mui/icons-material';

const AddStudent = () => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();
  const [teachers, setTeachers] = useState([]);
  const [message, setMessage] = useState('');
  const [importError, setImportError] = useState('');
  const navigate = useNavigate();
  const fileInputRef = React.useRef();
  const role = localStorage.getItem('role');

  useEffect(() => {
    const fetchTeachers = async () => {
      try {
        const res = await axios.get('/teachers/');
        setTeachers(Array.isArray(res.data) ? res.data : res.data.results || []);
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
        sx={{ mb: 2, ml: 20 }}
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
        <TextField
          fullWidth
          label="First Name"
          margin="normal"
          {...register('first_name', { required: 'First name is required' })}
          error={!!errors.first_name}
          helperText={errors.first_name?.message}
        />

        <TextField
          fullWidth
          label="Last Name"
          margin="normal"
          {...register('last_name', { required: 'Last name is required' })}
          error={!!errors.last_name}
          helperText={errors.last_name?.message}
        />

        <TextField
          fullWidth
          label="Phone Number"
          margin="normal"
          {...register('phone_number', {
            required: 'Phone number is required',
            pattern: {
              value: /^[0-9]{10}$/,
              message: 'Enter a valid 10-digit phone number',
            },
          })}
          error={!!errors.phone_number}
          helperText={errors.phone_number?.message}
        />

        <TextField
          fullWidth
          label="Roll Number"
          margin="normal"
          {...register('roll_number', { required: 'Roll number is required' })}
          error={!!errors.roll_number}
          helperText={errors.roll_number?.message}
        />

        <TextField
          fullWidth
          label="Class"
          margin="normal"
          {...register('student_class', { required: 'Class is required' })}
          error={!!errors.student_class}
          helperText={errors.student_class?.message}
        />

        <TextField
          fullWidth
          type="date"
          margin="normal"
          label="Date of Birth"
          InputLabelProps={{ shrink: true }}
          {...register('date_of_birth', { required: 'Date of birth is required' })}
          error={!!errors.date_of_birth}
          helperText={errors.date_of_birth?.message}
        />

        <TextField
          fullWidth
          type="date"
          margin="normal"
          label="Admission Date"
          InputLabelProps={{ shrink: true }}
          {...register('admission_date', { required: 'Admission date is required' })}
          error={!!errors.admission_date}
          helperText={errors.admission_date?.message}
        />

        <FormControl fullWidth margin="normal" error={!!errors.status}>
          <InputLabel>Status</InputLabel>
          <Select
            defaultValue="Active"
            label="Status"
            {...register('status', { required: 'Status is required' })}
          >
            <MenuItem value="Active">Active</MenuItem>
            <MenuItem value="Inactive">Inactive</MenuItem>
          </Select>
          {errors.status && <FormHelperText>{errors.status.message}</FormHelperText>}
        </FormControl>

        <TextField
          fullWidth
          label="Username"
          margin="normal"
          {...register('username', { required: 'Username is required' })}
          error={!!errors.username}
          helperText={errors.username?.message}
        />

        <TextField
          fullWidth
          label="Password"
          type="password"
          margin="normal"
          {...register('password', {
            required: 'Password is required',
            minLength: { value: 6, message: 'Minimum 6 characters required' },
          })}
          error={!!errors.password}
          helperText={errors.password?.message}
        />

        <TextField
          fullWidth
          label="Email"
          type="email"
          margin="normal"
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^\S+@\S+$/i,
              message: 'Enter a valid email address',
            },
          })}
          error={!!errors.email}
          helperText={errors.email?.message}
        />

        {role === 'admin' && (
          <FormControl fullWidth margin="normal" error={!!errors.assigned_teacher}>
            <InputLabel>Assigned Teacher</InputLabel>
            <Select
              defaultValue=""
              label="Assigned Teacher"
              {...register('assigned_teacher', { required: 'Assigned teacher is required' })}
            >
              {teachers.map((teacher) => (
                <MenuItem key={teacher.id} value={teacher.id}>
                  {teacher.first_name} {teacher.last_name}
                </MenuItem>
              ))}
            </Select>
            {errors.assigned_teacher && (
              <FormHelperText>{errors.assigned_teacher.message}</FormHelperText>
            )}
          </FormControl>
        )}

        <Button fullWidth type="submit" variant="contained" sx={{ mt: 3 }}>
          Add Student
        </Button>
      </Box>

      <Button variant="outlined" sx={{ ml: 30, mt: 2 }} onClick={() => navigate('/dashboard')}>
        Back
      </Button>
    </Container>
  );
};

export default AddStudent;
