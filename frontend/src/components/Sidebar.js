import AddIcon from '@mui/icons-material/Add';
import Divider from '@mui/material/Divider';
import GroupIcon from '@mui/icons-material/Group';
import SettingsIcon from '@mui/icons-material/Settings';
import Avatar from '@mui/material/Avatar';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';
import useAxios from '../utils/useAxios';
import { useEffect, useState } from 'react';

function Sidebar() {
  const axios = useAxios();
  const [chatGroups, setChatGroups] = useState([]);
  const navigate = useNavigate();
  const friendsText = 'Friends';
  const newChatGroupText = 'New Chat Group';

  useEffect(() => {
    axios.get('/api/chats/').then((response) => {
      setChatGroups(response.data);
    });
  }, []);

  return (
    <Box
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        backgroundColor: '#36393f'
      }}>
      <Box style={{ padding: '0px 16px ' }}>
        <List>
          <ListItem key={friendsText} disablePadding>
            <ListItemButton disableGutters key={friendsText} onClick={() => navigate('/dashboard')}>
              <ListItemIcon>
                <GroupIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary={friendsText} />
            </ListItemButton>
          </ListItem>
          <ListItem key={newChatGroupText} disablePadding>
            <ListItemButton disableGutters>
              <ListItemIcon>
                <AddIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary={newChatGroupText} />
            </ListItemButton>
          </ListItem>
        </List>
        <Divider />
        <List style={{ maxHeight: '68vh', overflowY: 'auto', overscrollBehavior: 'contain' }}>
          <ListItem key={-1} disablePadding>
            <ListItemText primaryTypographyProps={{ fontFamily: 'NotoSans' }}>
              CHAT GROUPS
            </ListItemText>
          </ListItem>
          {chatGroups.map((group) => {
            return (
              <ListItem key={group.id} disablePadding>
                <ListItemButton disableGutters>
                  <ListItemAvatar>
                    <Avatar>{group.name[0]}</Avatar>
                  </ListItemAvatar>
                  <ListItemText primary={group.name} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
      <Box
        sx={{
          padding: '0px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          bgcolor: '#2C2F33'
        }}>
        <Typography>username</Typography>
        <IconButton disableRipple disableFocusRipple>
          <SettingsIcon />
        </IconButton>
      </Box>
    </Box>
  );
}

export default Sidebar;
