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
  Box,
} from '@mui/material'
import api from '../api/axios'

const Teachers = () => {
  const [teachers, setTeachers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchTeachers = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await api.get('teachers/')  
        setTeachers(response.data)
      } catch (err) {
        if (err.response?.status === 401) {
          setError('❌ Unauthorized. Please login again.')
        } else {
          setError('❌ Failed to fetch teachers.')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchTeachers()
  }, [])

  return (
    <Container maxWidth="lg" sx={{ mt: 5 }}>
      <Typography variant="h4" gutterBottom align="center">
        Teachers
      </Typography>

      {loading && (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && teachers.length === 0 && !error && (
        <Alert severity="info">No teachers found.</Alert>
      )}

      {!loading && teachers.length > 0 && (
        <TableContainer component={Paper} sx={{ mt: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>SI.no</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Phone</TableCell>
                <TableCell>Subject</TableCell>
                <TableCell>Employee ID</TableCell>
                <TableCell>Date of Joining</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {teachers.map((t, index) => (
                <TableRow key={t.id}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{t.first_name} {t.last_name}</TableCell>
                  <TableCell>{t.email}</TableCell>
                  <TableCell>{t.phone}</TableCell>
                  <TableCell>{t.subject}</TableCell>
                  <TableCell>{t.e_id}</TableCell>
                  <TableCell>{new Date(t.doj).toLocaleDateString()}</TableCell>
                  <TableCell>{t.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  )
}

export default Teachers
