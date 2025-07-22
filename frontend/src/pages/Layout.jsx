// src/components/Layout.js
import { Outlet, useNavigate } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box, Drawer, IconButton, List, ListItem, ListItemText, GlobalStyles } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useEffect, useState } from 'react';

const defaultNavItems = [
  { label: 'View Students', path: '/students' },
  { label: 'Add Students', path: '/add-student' },
  { label: 'Manage Exams', path: '/teacher-exams' },
];

const Layout = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [navItems, setNavItems] = useState(defaultNavItems);
  const [username, setUsername] = useState('User');
  const navigate = useNavigate();

  useEffect(() => {
    const role = localStorage.getItem('role');
    const token = localStorage.getItem('token');

    let url = null;
    if (role === 'teacher') url = 'http://localhost:8000/people/teachers/me/';
    else if (role === 'student') url = 'http://localhost:8000/people/students/me/';
    else if (role === 'admin') url = 'http://localhost:8000/people/admins/me/';

    if (url && token) {
      fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          setUsername(data.first_name ? `${data.first_name} ${data.last_name || ''}` : data.username || 'User');
        })
        .catch(() => setUsername('User'));
    }

    // Set nav items
    if (role === 'student') {
      setNavItems([
        { label: 'View Details', path: '/student-details' },
        { label: 'View Exams', path: '/student-exams' },
      ]);
    } else if (role === 'admin') {
      setNavItems([
        { label: 'Add Student', path: '/add-student' },
        { label: 'Add Teacher', path: '/add-teacher' },
        { label: 'View Students', path: '/students' },
        { label: 'View Teachers', path: '/teachers' },
      ]);
    }
  }, []);

  const drawer = (
    <Box sx={{ width: 250 }} onClick={() => setDrawerOpen(false)}>
      <List>
        {navItems.map(item => (
          <ListItem button key={item.label} onClick={() => navigate(item.path)}>
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
        body: { margin: 0, padding: 0, width: '100vw', height: '100vh' },
        '#root': { width: '100vw', height: '100vh' },
      }} />
      <AppBar position="static" sx={{ bgcolor: '#232323', color: '#fff' }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>School Management</Typography>
          <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
            <IconButton color="inherit" onClick={() => setDrawerOpen(true)}>
              <MenuIcon />
            </IconButton>
          </Box>
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 2 }}>
            {navItems.map((item) => (
              <Button key={item.label} sx={{ color: '#fff' }} onClick={() => navigate(item.path)}>
                {item.label}
              </Button>
            ))}
          </Box>
          <Button
            variant="contained"
            sx={{ bgcolor: '#e6f2d6', color: '#232323', fontWeight: 600 }}
            onClick={() => {
              localStorage.clear();
              window.location.href = '/';
            }}
          >
            LOGOUT
          </Button>
        </Toolbar>
      </AppBar>
      <Drawer anchor="left" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        {drawer}
      </Drawer>
      <Box sx={{ height: 'calc(100vh - 64px)', overflow: 'auto', bgcolor: '#e6f2d6', p: 3 }}>
        <Outlet />
      </Box>
    </>
  );
};

export default Layout;
