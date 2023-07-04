import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import { useEffect } from 'react';
import useAxiosProtected from '../utils/useAxiosProtected';
import useFriendsListStore from '../utils/useFriendsListStore';
import FriendList from './FriendList';

function Friends() {
  const friendsList = useFriendsListStore((state) => state.friendsList);
  const setFriendsList = useFriendsListStore((state) => state.setFriendsList);
  const axios = useAxiosProtected();

  useEffect(() => {
    if (!friendsList) {
      axios.get('/api/users/me/friends/').then((response) => {
        setFriendsList(response.data);
      });
    }
  }, []);

  return (
    <Box style={{ display: 'flex', flexDirection: 'column', padding: '16px 32px 16px 32px' }}>
      <TextField
        size="small"
        variant="outlined"
        padding="0px"
        placeholder="Search"
        style={{ marginBottom: '16px' }}
      />
      <Typography style={{ marginBottom: '8px' }}>Friends</Typography>
      <Divider />
      {<FriendList list={friendsList || []} isPending={false} />}
    </Box>
  );
}

export default Friends;
