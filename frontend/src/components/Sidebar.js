import PropTypes from 'prop-types';
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
import useAxiosProtected from '../utils/useAxiosProtected';
import BaseFormDialog from './BaseFormDialog';
import { useCallback, useContext, useEffect, useState } from 'react';
import { Button, DialogActions, DialogContent, DialogContentText, TextField } from '@mui/material';
import AuthContext from '../utils/AuthContext';
import useChatGroupStore from '../utils/useChatGroupStore';

function Sidebar() {
  const axios = useAxiosProtected();
  const chatGroups = useChatGroupStore((state) => state.chatGroups);
  const setChatGroups = useChatGroupStore((state) => state.setChatGroups);
  const [openDialog, setOpenDialog] = useState(false);
  const [prevClickedGroup, setPrevClickedGroup] = useState(-1);
  const navigate = useNavigate();
  const friendsText = 'Friends';
  const newChatGroupText = 'New Chat Group';

  const handleOnChatGroupClick = useCallback((groupId) => {
    setPrevClickedGroup(groupId);
    navigate(`/dashboard/chats/${groupId}`);
  });

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
            <ListItemButton disableGutters onClick={() => navigate('/dashboard')}>
              <ListItemIcon>
                <GroupIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary={friendsText} />
            </ListItemButton>
          </ListItem>
          <ListItem key={newChatGroupText} disablePadding>
            <ListItemButton
              disableGutters
              onClick={() => setOpenDialog((prevDialog) => !prevDialog)}>
              <ListItemIcon>
                <AddIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary={newChatGroupText} />
            </ListItemButton>
            <NewChatGroupFormDialog open={openDialog} setOpen={setOpenDialog} />
          </ListItem>
        </List>
        <Divider />
        <List style={{ maxHeight: '80vh', overflowY: 'auto', overscrollBehavior: 'contain' }}>
          <ListItem key={-1} disablePadding>
            <ListItemText primaryTypographyProps={{ fontFamily: 'NotoSans' }}>
              CHAT GROUPS
            </ListItemText>
          </ListItem>
          {chatGroups.map((group) => {
            return (
              <ListItem key={group.id} disablePadding>
                <ListItemButton
                  sx={{
                    bgcolor: prevClickedGroup === group.id ? 'secondary.dark' : 'secondary.main',
                    paddingLeft: '8px'
                  }}
                  onClick={() => handleOnChatGroupClick(group.id)}>
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

function NewChatGroupFormDialog({ open, setOpen }) {
  const axios = useAxiosProtected();
  const { getUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const addChatGroup = useChatGroupStore((state) => state.addChatGroup);
  const handleClose = useCallback((e) => {
    e.preventDefault();
    if (e.target.name) {
      const name = e.target.name.value;
      axios
        .post('/api/chats/', { owner: getUser()?.user_id, name: name })
        .then((response) => {
          const id = response?.data['id'];
          // FIXME: The backend should return the same object keys that are seen when
          // fetching the chat group list!
          addChatGroup({ id: id, name: name });
          navigate(`/dashboard/chats/${id}`);
        })
        .catch(() => console.log('Unable to create a new chat group!'));
    }
    setOpen(false);
  });

  return (
    <BaseFormDialog
      open={open}
      title={'Customize your new chat group'}
      handleClose={handleClose}
      component={
        <form onSubmit={handleClose}>
          <DialogContent>
            <DialogContentText>
              Give your chat group its own identity by giving it a name
            </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              name="name"
              label="Chat group name"
              defaultValue="New Chat Group"
              type="text"
              fullWidth
              variant="standard"
            />
          </DialogContent>
          <DialogActions>
            <Button variant="outlined" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" color="primary" variant="outlined">
              Create
            </Button>
          </DialogActions>
        </form>
      }
    />
  );
}

NewChatGroupFormDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired
};

export default Sidebar;
