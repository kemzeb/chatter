import { Outlet } from 'react-router-dom';
import Box from '@mui/material/Box';
import ActivityBar from './ActivityBar';

function ActivityView() {
  return (
    <Box sx={{ flexGrow: '2', bgcolor: '#23272A' }}>
      <ActivityBar />
      <Outlet />
    </Box>
  );
}

export default ActivityView;
