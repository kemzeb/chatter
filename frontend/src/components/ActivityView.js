import { Outlet } from 'react-router-dom';
import Box from '@mui/material/Box';
import ActivityBar from './ActivityBar';

function ActivityView() {
  return (
    <Box style={{ display: 'grid', gridTemplateRows: '48px auto', backgroundColor: '#23272A' }}>
      <ActivityBar />
      <Outlet />
    </Box>
  );
}

export default ActivityView;
