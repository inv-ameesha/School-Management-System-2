import { useEffect, useState } from 'react'
import {
  Container,
  Typography,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  Paper,
  CircularProgress,
  Alert,
  Box,Button
} from '@mui/material'
import api from '../api/axios'
import { useNavigate } from 'react-router-dom'

function Students() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate();
  useEffect(() => {
    const fetchStudents = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await api.get('students/')
        setStudents(response.data)
      } catch (err) {
        if (err.response?.status === 401) {
          setError('Unauthorized. Please login again.')
        } else {
          setError('Failed to fetch student data.')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchStudents()
  }, [])

  return (
    <div>
      <Container maxWidth="lg" sx={{ mt: 5 }}>
        <Typography variant="h4" gutterBottom align="center">
          Students
        </Typography>

        {loading && (
          <Box display="flex" justifyContent="center" mt={4}>
            <CircularProgress />
          </Box>
        )}

        {error && <Alert severity="error">{error}</Alert>}

        {!loading && students.length === 0 && !error && (
          <Alert severity="info">No students found.</Alert>
        )}

        {!loading && students.length > 0 && (
          <TableContainer component={Paper} sx={{ mt: 3 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>SI.no</TableCell>
                  <TableCell>Full Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Roll No</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Date of Birth</TableCell>
                  <TableCell>Admission Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Assigned Teacher</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {students.map((s, index) => (
                  <TableRow key={s.id}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{s.first_name} {s.last_name}</TableCell>
                    <TableCell>{s.email}</TableCell>
                    <TableCell>{s.phone_number}</TableCell>
                    <TableCell>{s.roll_number}</TableCell>
                    <TableCell>{s.student_class}</TableCell>
                    <TableCell>{new Date(s.date_of_birth).toLocaleDateString()}</TableCell>
                    <TableCell>{new Date(s.admission_date).toLocaleDateString()}</TableCell>
                    <TableCell>{s.status}</TableCell>
                    <TableCell>{s.assigned_teacher_name || 'N/A'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Container>
      <Button variant="outlined" sx={{ ml: 2, mt: 2 }} onClick={() => navigate('/dashboard')}>
        Back
      </Button>
    </div>


  )
}

export default Students
