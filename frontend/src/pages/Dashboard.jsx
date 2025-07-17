

import '../App.css';
import { Box,Button,Container, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom'

const Dashboard = () =>{
    const navigate = useNavigate()
    return(
        <Container>
            <Box>
                <Typography variant='h4' gutterBottom>Admin Dasboard</Typography>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 2, mt: 3 }}>
                <Button variant="contained" onClick={()=>navigate('/students')}>View Students</Button>
                <Button variant="contained" onClick={()=>navigate('/teachers')}>View teachers</Button>
                <Button variant="contained" onClick={()=>navigate('/add-student')}>Add Students</Button>
                <Button variant="contained" onClick={()=>navigate('/add-teacher')}>Add teachers</Button>
            </Box>
        </Container>
    )
}

export default Dashboard;