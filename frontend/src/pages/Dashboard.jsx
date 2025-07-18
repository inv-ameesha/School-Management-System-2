import '../App.css';
import { Box, Button, Container, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const role = localStorage.getItem('role'); // Get role from localStorage

  return (
    <Container>
      <Box textAlign="center" mt={4}>
        <Typography variant='h4' gutterBottom>
          {role === 'admin' ? 'Admin' : 'Teacher'} Dashboard
        </Typography>
      </Box>

      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 2,
          mt: 4,
        }}
      >
        <Button variant="contained" onClick={() => navigate('/students')}>
          View Students
        </Button>

        {role === 'admin' && (
          <Button variant="contained" onClick={() => navigate('/teachers')}>
            View Teachers
          </Button>
        )}

        <Button variant="contained" onClick={() => navigate('/add-student')}>
          Add Students
        </Button>

        {role === 'admin' && (
          <Button variant="contained" onClick={() => navigate('/add-teacher')}>
            Add Teachers
          </Button>
        )}
      </Box>
    </Container>
  );
};

export default Dashboard;
