import Sidebar from '../components/Sidebar';
import ActivityView from '../components/ActivityView';
import Box from '@mui/material/Box';

function Dashboard() {
  return (
    <Box
      style={{
        display: 'grid',
        gridTemplateColumns: '252px 1fr',
        minWidth: '100vw',
        minHeight: '100vh'
      }}>
      <Sidebar />
      <ActivityView />
    </Box>
  );
}

export default Dashboard;
