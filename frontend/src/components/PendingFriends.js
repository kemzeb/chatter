import { Box, Divider, Typography } from '@mui/material';
import useAxiosProtected from '../utils/useAxiosProtected';
import FriendList from './FriendList';
import { useEffect } from 'react';
import usePendingFriendsStore from '../utils/usePendingFriendsStore';

function PendingFriends() {
  const pendingFriends = usePendingFriendsStore((state) => state.pendingFriends);
  const setPendingFriends = usePendingFriendsStore((state) => state.setPendingFriends);
  const axios = useAxiosProtected();

  useEffect(() => {
    if (!pendingFriends) {
      axios.get('/api/users/me/friendrequests/').then((response) => {
        setPendingFriends(response.data);
      });
    }
  }, []);

  return (
    <Box style={{ display: 'flex', flexDirection: 'column', padding: '16px 32px 16px 32px' }}>
      <Typography style={{ marginBottom: '8px' }}>Pending Requests</Typography>
      <Divider />
      <FriendList list={pendingFriends || []} isPending={true} />
    </Box>
  );
}

export default PendingFriends;
