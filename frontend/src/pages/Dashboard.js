import Sidebar from '../components/Sidebar';
import ActivityView from '../components/ActivityView';
import Box from '@mui/material/Box';
import { useContext } from 'react';
import useSubscriber from '../utils/useSubscriber';
import AuthContext from '../utils/AuthContext';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const { getAuthTokens } = useContext(AuthContext);
  const tokens = getAuthTokens();
  const navigate = useNavigate();
  if (!tokens) navigate('/');

  useSubscriber(`ws://localhost:8000/ws/chat?token=${tokens.access}`, (message) =>
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
