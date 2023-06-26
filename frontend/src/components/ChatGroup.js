import Box from '@mui/material/Box';
import { useContext } from 'react';
import AuthContext from '../utils/AuthContext';
import { List, ListItem, Typography, TextField } from '@mui/material';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import { useNavigate } from 'react-router-dom';
import { getExampleMessages, getExampleFriends } from '../utils/examples';

function ChatGroup() {
  const { getUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const messages = getExampleMessages();
  const members = getExampleFriends();
  const user = getUser();

  if (!user) navigate('/');

  return (
    <Box
      style={{
        display: 'grid',
        gridTemplateColumns: '2fr 240px'
      }}>
      <Box style={{ display: 'flex', flexDirection: 'column', backgroundColor: ' #595959' }}>
        <List
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: '85vh',
            overflow: 'auto',
            overscrollBehavior: 'contain'
          }}>
          {messages.map((msg) => {
            const alignSelf = msg.user == user.user_id ? 'flex-end' : 'flex-start';
            return (
              <ListItem
                key={msg.id}
                style={{
                  alignSelf: alignSelf,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: alignSelf
                }}>
                <Typography fontSize={14} fontWeight={500}>
                  {msg.username}
                </Typography>
                <Typography fontSize={14}>{msg.message}</Typography>
              </ListItem>
            );
          })}
        </List>
        <TextField
          size="small"
          variant="outlined"
          placeholder="Search"
          style={{ margin: '8px 16px 16px 16px' }}
        />
      </Box>
      <Box style={{ padding: '20px' }}>
        <Typography fontSize={15} style={{ marginBottom: '4px' }}>
          Members
        </Typography>
        <List
          style={{
            display: 'flex',
            flexDirection: 'column',
            maxHeight: '85vh',
            overflow: 'auto',
            overscrollBehavior: 'contain'
          }}>
          {members.map((member) => {
            return (
              <ListItem key={member.id} disableGutters>
                <ListItemAvatar>
                  <Avatar style={{ width: '34px', height: '32px' }}>
                    {member.username.charAt(0).toLowerCase()}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText primary={member.username} fontSize={12} />
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Box>
  );
}

export default ChatGroup;
