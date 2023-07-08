import Sidebar from '../components/Sidebar';
import ActivityView from '../components/ActivityView';
import Box from '@mui/material/Box';
import useSubscriber from '../utils/useSubscriber';
import useMessageStore from '../utils/useMessageStore';
import usePendingFriendsStore from '../utils/usePendingFriendsStore';
import useFriendsListStore from '../utils/useFriendsListStore';
import { useContext } from 'react';
import AuthContext from '../utils/AuthContext';
import useChatGroupStore from '../utils/useChatGroupStore';
import useAxiosProtected from '../utils/useAxiosProtected';
import useMembersStore from '../utils/useMembersStore';

function Dashboard() {
  const axios = useAxiosProtected();
  const { getUser } = useContext(AuthContext);
  const user = getUser();
  const addChatGroup = useChatGroupStore((state) => state.addChatGroup);
  const addMessage = useMessageStore((state) => state.addMessage);
  const addPendingFriend = usePendingFriendsStore((state) => state.addPendingFriend);
  const removePendingFriend = usePendingFriendsStore((state) => state.removePendingFriend);
  const addFriend = useFriendsListStore((state) => state.addFriend);
  const addMember = useMembersStore((state) => state.addMember);

  useSubscriber((event) => {
    const message = event.message;
    switch (event.event_type) {
      case 'group:add': {
        if (user.user_id === message.user.id) {
          // We must add the chat group into its respective store since it doesn't
          // exist yet.
          axios.get(`/api/chats/${message.chat_group}/`).then((response) => {
            addChatGroup(response.data);
          });
        } else {
          addMember(message);
        }
        break;
      }
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
        if (user.user_id === message.requester.id) {
          addFriend(message.addressee);
        } else {
          removePendingFriend(message.id);
          addFriend(message.requester);
        }
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
