import '../App.css';
import { useState, useEffect } from 'react';
import { Typography, Box } from '@mui/material';

const Dashboard = () => {
  const [username, setUsername] = useState('User');

  useEffect(() => {
    const fetchUsername = async () => {
      const role = localStorage.getItem('role');
      const token = localStorage.getItem('token');
      let url = null;

      if (role === 'teacher') url = 'http://localhost:8000/people/teachers/me/';
      else if (role === 'student') url = 'http://localhost:8000/people/students/me/';
      else if (role === 'admin') url = 'http://localhost:8000/people/admins/me/';

      if (url && token) {
        try {
          const res = await fetch(url, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (res.ok) {
            const data = await res.json();
            setUsername(data.first_name ? `${data.first_name} ${data.last_name || ''}` : data.username || 'User');
          } else {
            setUsername('User');
          }
        } catch {
          setUsername('User');
        }
      } else {
        setUsername('User');
      }
    };

    fetchUsername();
  }, []);

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: { xs: 'column', md: 'row' },
      alignItems: 'center',
      justifyContent: 'center',
      height: 'calc(100vh - 64px)',
      width: '100vw',
      bgcolor: '#e6f2d6',
      overflow: 'hidden',
      gap: { xs: 4, md: 10 },
      width:'100%'
    }}>
      <Box sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'flex-start',
        width: { xs: '90vw', md: 500 },
        maxWidth: 600,
      }}>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 3, color: '#232323', lineHeight: 1.1, textAlign: 'left', width: '100%' }}>
          {`Welcome ${username}`}
        </Typography>
      </Box>
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: { xs: '90vw', md: 350 },
        minWidth: 320,
      }}>
        <Box sx={{ width: 320, height: 400, bgcolor: '#fff', borderRadius: 4, boxShadow: 3, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <img
            src="/school1.jpg"
            alt="School Visual"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              borderRadius: '16px',
            }}
          />
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;