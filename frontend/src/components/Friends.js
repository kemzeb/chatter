import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import ListItemText from '@mui/material/ListItemText';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { IconButton } from '@mui/material';
import { useEffect, useState } from 'react';
import useAxiosProtected from '../utils/useAxiosProtected';

function Friends() {
  const [friendsList, setFriendsList] = useState([]);
  const axios = useAxiosProtected();

  useEffect(() => {
    axios.get('/api/users/me/friends/').then((response) => {
      setFriendsList(response.data);
    });
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
      <List style={{ maxHeight: '78vh', overflowY: 'auto', overscrollBehavior: 'contain' }}>
        {friendsList.map((friend) => {
          return (
            <ListItem key={friend.id} disableGutters divider>
              <ListItemAvatar>
                <Avatar>{friend.username.charAt(0).toLowerCase()}</Avatar>
              </ListItemAvatar>
              <ListItemText primary={friend.username} />
              <IconButton>
                <MoreVertIcon color="primary" />
              </IconButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
}

export default Friends;
