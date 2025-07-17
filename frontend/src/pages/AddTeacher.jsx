import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
} from '@mui/material'
import { useForm } from 'react-hook-form'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const AddTeacher = () => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm()

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const navigate = useNavigate()

  const onSubmit = async (data) => {
    try {
      const token = localStorage.getItem('token')  
      const response = await fetch('http://localhost:8000/people/teachers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Failed to add teacher')
      }

      setSuccess('Teacher added successfully')
      setError('')
      reset()

      setTimeout(() => navigate('/dashboard'), 2000)
    } catch (err) {
      console.error(err)
      setError('Failed to add teacher')
      setSuccess('')
    }
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Typography variant="h5" gutterBottom>
        Add Teacher
      </Typography>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Box display="flex" flexDirection="column" gap={2}>
          <TextField
            label="First Name"
            id="first_name"
            name="first_name"
            {...register('first_name', { required: true })}
            error={!!errors.first_name}
            helperText={errors.first_name && 'First name is required'}
          />
          <TextField
            label="Last Name"
            id="last_name"
            name="last_name"
            {...register('last_name', { required: true })}
            error={!!errors.last_name}
            helperText={errors.last_name && 'Last name is required'}
          />
          <TextField
            label="Email"
            id="email"
            name="email"
            type="email"
            {...register('email', { required: true })}
            error={!!errors.email}
            helperText={errors.email && 'Email is required'}
          />
          <TextField
            label="Phone"
            id="phone"
            name="phone"
            {...register('phone', { required: true })}
            error={!!errors.phone}
            helperText={errors.phone && 'Phone is required'}
          />
          <TextField
            label="Subject"
            id="subject"
            name="subject"
            {...register('subject', { required: true })}
            error={!!errors.subject}
            helperText={errors.subject && 'Subject is required'}
          />
          <TextField
            label="Employee ID"
            id="e_id"
            name="e_id"
            {...register('e_id', { required: true })}
            error={!!errors.e_id}
            helperText={errors.e_id && 'Employee ID is required'}
          />
          <TextField
            label="Date of Joining"
            id="doj"
            name="doj"
            type="date"
            {...register('doj', { required: true })}
            InputLabelProps={{ shrink: true }}
            error={!!errors.doj}
            helperText={errors.doj && 'Date of joining is required'}
          />
          <TextField
            label="Status"
            id="status"
            name="status"
            {...register('status', { required: true })}
            error={!!errors.status}
            helperText={errors.status && 'Status is required'}
          />
          <TextField
            label="Username"
            id="username"
            name="username"
            {...register('username', { required: true })}
            error={!!errors.username}
            helperText={errors.username && 'Username is required'}
          />
          <TextField
            label="Password"
            id="password"
            name="password"
            type="password"
            {...register('password', { required: true })}
            error={!!errors.password}
            helperText={errors.password && 'Password is required'}
          />

          <Button variant="contained" type="submit">
            Add Teacher
          </Button>
        </Box>
      </form>

      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
    </Container>
  )
}

export default AddTeacher
