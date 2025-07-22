import '../App.css';
import { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, GlobalStyles, Drawer, IconButton, List, ListItem, ListItemText } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useNavigate } from 'react-router-dom';

const navItems = [
  { label: 'View Students', path: '/students' },
  { label: 'Add Students', path: '/add-student' },
  { label: 'Manage Exams', path: '/teacher-exams' },
];

const Dashboard = () => {
  const [username, setUsername] = useState('User');
  const [navItemsState, setNavItemsState] = useState(navItems);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();

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

    const role = localStorage.getItem('role');
    if (role === 'student') {
      setNavItemsState([
        { label: 'View Details', path: '/student-details' },
        { label: 'View Exams', path: '/student-exams' },
      ]);
    } else if (role === 'admin') {
      setNavItemsState([
        { label: 'Add Student', path: '/add-student' },
        { label: 'Add Teacher', path: '/add-teacher' },
        { label: 'View Students', path: '/students' },
        { label: 'View Teachers', path: '/teachers' },
      ]);
    } else {
      setNavItemsState(navItems);
    }
  }, []);

  const drawer = (
    <Box sx={{ width: 250 }} role="presentation" onClick={() => setDrawerOpen(false)}>
      <List>
        {navItemsState.map((item) => (
          <ListItem button key={item.label} onClick={() => { if (item.path) navigate(item.path); }}>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <>
      <GlobalStyles styles={{
        html: { width: '100vw', height: '100vh', overflow: 'hidden' },
        body: { width: '100vw', height: '100vh', overflow: 'hidden', margin: 0, padding: 0 },
        '#root': { width: '100vw', height: '100vh', overflow: 'hidden' },
      }} />
      <Box sx={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', bgcolor: '#f5f3ef', overflow: 'hidden', p: 0, m: 0 }}>
        <AppBar position="static" sx={{ bgcolor: '#232323', color: '#fff', boxShadow: 0, width: '100vw', m: 0 }}>
          <Toolbar sx={{ justifyContent: 'space-between', minHeight: 64 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: 2 }}>
              School Management
            </Typography>
            <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
              <IconButton color="inherit" edge="start" onClick={() => setDrawerOpen(true)}>
                <MenuIcon />
              </IconButton>
            </Box>
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 3 }}>
              {navItemsState.map((item) => (
                <Button
                  key={item.label}
                  sx={{ color: '#fff', fontWeight: 500, fontSize: 16 }}
                  disableRipple
                  onClick={() => {
                    if (item.path) navigate(item.path);
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                sx={{ bgcolor: '#e6f2d6', color: '#232323', fontWeight: 600, px: 3, '&:hover': { bgcolor: '#d2e6b8' } }}
                onClick={() => {
                  localStorage.clear();
                  window.location.href='/'
                }}
              >
                LOGOUT
              </Button>
            </Box>
          </Toolbar>
        </AppBar>
        <Drawer anchor="left" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
          {drawer}
        </Drawer>
        <Box sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          alignItems: 'center',
          justifyContent: 'center',
          height: 'calc(100vh - 64px)',
          width: '100vw',
          bgcolor: '#e6f2d6',
          m: 0,
          p: 0,
          overflow: 'hidden',
          gap: { xs: 4, md: 10 },
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
      </Box>
    </>
  );
};

export default Dashboard;
