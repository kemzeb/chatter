import Sidebar from '../components/Sidebar';
import ActivityView from '../components/ActivityView';
import Box from '@mui/material/Box';
import useSubscriber from '../utils/useSubscriber';
import useMessageStore from '../utils/useMessageStore';
import usePendingFriendsStore from '../utils/usePendingFriendsStore';
import useFriendsListStore from '../utils/useFriendsListStore';
import { useContext } from 'react';
import AuthContext from '../utils/AuthContext';

function Dashboard() {
  const { getUser } = useContext(AuthContext);
  const user = getUser();
  const addMessage = useMessageStore((state) => state.addMessage);
  const addPendingFriend = usePendingFriendsStore((state) => state.addPendingFriend);
  const removePendingFriend = usePendingFriendsStore((state) => state.removePendingFriend);
  const addFriend = useFriendsListStore((state) => state.addFriend);

  useSubscriber((event) => {
    const message = event.message;
    switch (event.event_type) {
      case 'group:message':
        addMessage(message);
        break;
      case 'user:friendrequest':
        addPendingFriend(message);
        break;
      case 'user:reject':
        removePendingFriend(message.id);
        break;
      case 'user:accept':
        removePendingFriend(message.id);
        user.id === message.requester.id
          ? addFriend(message.addressee)
          : addFriend(message.requester);
        break;
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
