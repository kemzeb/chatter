import Sidebar from '../components/Sidebar';
import ActivityView from '../components/ActivityView';
import Box from '@mui/material/Box';
import useSubscriber from '../utils/useSubscriber';
import useMessageStore from '../utils/useMessageStore';

function Dashboard() {
  const addMessageFromEvent = useMessageStore((state) => state.addMessageFromEvent);

  useSubscriber((event) => {
    switch (event.event_type) {
      case 'group:message':
        addMessageFromEvent(event);
    }
  });

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
