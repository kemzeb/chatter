import Sidebar from '../components/Sidebar';
import ActivityView from '../components/ActivityView';
import Box from '@mui/material/Box';

function Dashboard() {
  return (
    <Box style={{ display: 'flex', minWidth: '100vw', minHeight: '100vh' }}>
      <Sidebar />
      <ActivityView />
    </Box>
  );
}

export default Dashboard;
