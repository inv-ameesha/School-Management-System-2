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
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Pagination,
} from '@mui/material'
import api from '../api/axios'
import { useNavigate } from 'react-router-dom'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'

const Teachers = () => {
  const [teachers, setTeachers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleteId, setDeleteId] = useState(null)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const navigate = useNavigate()
  const isAdmin = localStorage.getItem('role') === 'admin'

  useEffect(() => {
    const fetchTeachers = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await api.get(`teachers/?page=${page}`)
        setTeachers(response.data.results)
        setTotalPages(Math.ceil(response.data.count / 5)) // Assuming 5 per page
      } catch (err) {
        if (err.response?.status === 401) {
          setError('Unauthorized. Please login again.')
        } else {
          setError('Failed to fetch teachers.')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchTeachers()
  }, [page])

  const handleDelete = async () => {
    try {
      await api.delete(`teachers/${deleteId}/`)
      setTeachers(prev => prev.filter(t => t.id !== deleteId))
      setConfirmOpen(false)
    } catch (err) {
      setError('Failed to delete teacher.')
    }
  }

  const handlePageChange = (event, value) => {
    setPage(value)
  }

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
        <>
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
                  {isAdmin && <TableCell>Actions</TableCell>}
                </TableRow>
              </TableHead>
              <TableBody>
                {teachers.map((t, index) => (
                  <TableRow key={t.id}>
                    <TableCell>{(page - 1) * 5 + index + 1}</TableCell>
                    <TableCell>{t.first_name} {t.last_name}</TableCell>
                    <TableCell>{t.email}</TableCell>
                    <TableCell>{t.phone}</TableCell>
                    <TableCell>{t.subject}</TableCell>
                    <TableCell>{t.e_id}</TableCell>
                    <TableCell>{new Date(t.doj).toLocaleDateString()}</TableCell>
                    <TableCell>{t.status}</TableCell>
                    {isAdmin && (
                      <TableCell>
                        <IconButton onClick={() => navigate(`/edit-teacher/${t.id}`)}><EditIcon /></IconButton>
                        <IconButton onClick={() => { setDeleteId(t.id); setConfirmOpen(true); }}><DeleteIcon /></IconButton>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Box display="flex" justifyContent="center" mt={3}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={handlePageChange}
              color="primary"
            />
          </Box>
        </>
      )}

      <Button variant="outlined" sx={{ ml: 70, mt: 2 }} onClick={() => navigate('/dashboard')}>
        Back
      </Button>

      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <DialogTitle>Delete Teacher</DialogTitle>
        <DialogContent>Are you sure you want to delete this teacher?</DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>Cancel</Button>
          <Button color="error" onClick={handleDelete}>Delete</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Teachers
