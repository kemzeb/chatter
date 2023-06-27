import Box from '@mui/material/Box';
import { useContext, useEffect, useState } from 'react';
import AuthContext from '../utils/AuthContext';
import { List, ListItem, Typography, TextField } from '@mui/material';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import { useNavigate, useParams } from 'react-router-dom';
import useAxiosProtected from '../utils/useAxiosProtected';

function ChatGroup() {
  const { getUser } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [chatMessage, setChatMessage] = useState('');
  const axios = useAxiosProtected();
  const navigate = useNavigate();
  const { id } = useParams();
  const [members, setMembers] = useState([]);
  const user = getUser();

  if (!user) navigate('/');

  const handleTextInput = (event) => {
    if (event.key == 'Enter' && event.target.value) {
      axios.post(`/api/chats/${id}/messages/`, {
        message: event.target.value
      });
      setChatMessage('');
    }
  };

  useEffect(() => {
    axios.get(`/api/chats/${id}/messages/`).then((response) => {
      setMessages(response.data);
    });
    axios.get(`/api/chats/${id}/members/`).then((response) => {
      setMembers(response.data);
    });
  }, [id]);

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
            const alignSelf = msg.user.id == user.user_id ? 'flex-end' : 'flex-start';
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
                  {msg.user.username}
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
          value={chatMessage}
          style={{ margin: '8px 16px 16px 16px' }}
          onKeyDown={handleTextInput}
          onChange={(event) => setChatMessage(event.target.value)}
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
              <ListItem key={member.user.id} disableGutters>
                <ListItemAvatar>
                  <Avatar style={{ width: '34px', height: '32px' }}>
                    {member.user.username.charAt(0).toLowerCase()}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText primary={member.user.username} fontSize={12} />
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Box>
  );
}

export default ChatGroup;
