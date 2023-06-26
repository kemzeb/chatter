import Sidebar from '../components/Sidebar';
import ActivityView from '../components/ActivityView';
import Box from '@mui/material/Box';
import { useContext } from 'react';
import useSubscriber from '../utils/useSubscriber';
import AuthContext from '../utils/AuthContext';

function Dashboard() {
  const { authTokens } = useContext(AuthContext);

  useSubscriber(`ws://localhost:8000/ws/chat?token=${authTokens?.access}`, (message) =>
    console.log(message)
  );

  return (
    <Box
      style={{
        display: 'grid',
        gridTemplateColumns: '252px 1fr',
        width: '100vw',
        height: '100vh'
      }}>
      <Sidebar />
      <ActivityView />
    </Box>
  );
}

export default Dashboard;
