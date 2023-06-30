import Box from '@mui/material/Box';
import { useContext, useEffect, useRef, useState } from 'react';
import AuthContext from '../utils/AuthContext';
import { List, ListItem, Typography, TextField } from '@mui/material';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import { useNavigate, useParams } from 'react-router-dom';
import useAxiosProtected from '../utils/useAxiosProtected';
import { renderDateTime } from '../utils/utils';
import useMessageStore from '../utils/useMessageStore';

function ChatGroup() {
  const { getUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const { id } = useParams();
  const messages = useMessageStore((state) => state.chatGroups[id]);
  const setMessageList = useMessageStore((state) => state.setMessageList);
  const [chatMessage, setChatMessage] = useState('');
  const [members, setMembers] = useState([]);
  const axios = useAxiosProtected();
  const bottomScrollRef = useRef();
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

  const scrollToBottom = () => bottomScrollRef.current.scrollIntoView({ behavior: 'auto' });

  useEffect(() => {
    if (!messages) {
      axios.get(`/api/chats/${id}/messages/`).then((response) => setMessageList(id, response.data));
    }

    axios.get(`/api/chats/${id}/members/`).then((response) => {
      setMembers(response.data);
    });
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
          {messages?.map((msg) => {
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
                <Box
                  style={{
                    display: 'flex',
                    gap: '4px',
                    alignItems: 'center'
                  }}>
                  <Typography component="div" fontSize={14} fontWeight={700}>
                    {msg.user.username}
                  </Typography>
                  <Typography component="div" fontSize={12} fontWeight={200}>
                    {' '}
                    {renderDateTime(msg.created)}
                  </Typography>
                </Box>
                <Typography fontSize={14}>{msg.message}</Typography>
              </ListItem>
            );
          })}
          <div ref={bottomScrollRef} />
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
