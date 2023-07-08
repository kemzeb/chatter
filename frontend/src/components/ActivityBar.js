import PropTypes from 'prop-types';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import Box from '@mui/material/Box';
import GroupIcon from '@mui/icons-material/Group';
import ForumIcon from '@mui/icons-material/Forum';
import Typography from '@mui/material/Typography';
import { useCallback, useEffect, useState } from 'react';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import {
  DialogActions,
  DialogContent,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  TextField
} from '@mui/material';
import BaseFormDialog from './BaseFormDialog';
import useAxiosProtected from '../utils/useAxiosProtected';

function ActivityBar() {
  const location = useLocation();
  const [path, setPath] = useState(location.pathname);

  useEffect(() => {
    setPath(location.pathname);
  }, [location]);

  return (
    <>
      <Box
        style={{
          display: 'flex',
          alignItems: 'center',
          padding: '8px',
          backgroundColor: '#424549'
        }}>
        {(path.startsWith('/dashboard/chats') && <ChatGroupSpecificBar />) || <FriendSpecificBar />}
      </Box>
    </>
  );
}

function FriendSpecificBar() {
  const navigate = useNavigate();
  const [openDialog, setOpenDialog] = useState(false);

  return (
    <Box style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <GroupIcon color="primary" />
      <Typography>Friends</Typography>
      <Divider flexItem orientation="vertical" />
      <Button variant="text" onClick={() => navigate('/dashboard')}>
        <Typography color="text.primary">All</Typography>
      </Button>
      <Button variant="text" onClick={() => setOpenDialog((prev) => !prev)}>
        <Typography color="text.primary">Add</Typography>
      </Button>
      <Button variant="text" onClick={() => navigate('/dashboard/pending')}>
        <Typography color="text.primary">Pending</Typography>
      </Button>
      <FriendRequestForumDialog open={openDialog} setOpen={setOpenDialog} />
    </Box>
  );
}

function FriendRequestForumDialog({ open, setOpen }) {
  const axios = useAxiosProtected();
  const handleClose = useCallback((e) => {
    e.preventDefault();
    if (e.target.addressee) {
      const username = e.target.addressee.value;
      axios
        .post('/api/users/me/friendrequests/', { username: username })
        .catch(() => console.error('Unable to send a friend request!'));
    }
    setOpen(false);
  });

  return (
    <BaseFormDialog
      open={open}
      title="Send a friend request to a user"
      handleClose={handleClose}
      component={
        <form onSubmit={handleClose}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              name="addressee"
              label="Enter a username here."
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
              Send Friend Request
            </Button>
          </DialogActions>
        </form>
      }
    />
  );
}

FriendRequestForumDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired
};

function ChatGroupSpecificBar() {
  const [openDialog, setOpenDialog] = useState(false);

  return (
    <Box style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <ForumIcon color="primary" />
      <Typography>Chat Group</Typography>
      <Divider flexItem orientation="vertical" />
      <Button variant="text" disableFocusRipple onClick={() => setOpenDialog((prev) => !prev)}>
        <Typography color="text.primary">Add Member</Typography>
      </Button>
      <AddMemberForumDialog open={openDialog} setOpen={setOpenDialog} />
    </Box>
  );
}

function AddMemberForumDialog({ open, setOpen }) {
  const axios = useAxiosProtected();
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState([]);
  const { id } = useParams();
  const handleResultClick = useCallback((friendId) => {
    axios.post(`/api/chats/${id}/members/`, { id: friendId });
    setOpen(false);
  });

  useEffect(() => {
    if (searchText.length > 0) {
      axios
        .get(`/api/users/me/friends/search/?q=${searchText}`)
        .then((response) => setResults(response.data['results']));
    }
  }, [searchText]);

  return (
    <BaseFormDialog
      open={open}
      title="Add a friend to your chat group"
      handleClose={() => setOpen(false)}
      component={
        <>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Enter your friend's username here."
              type="text"
              fullWidth
              variant="standard"
              onChange={(e) => setSearchText(e.target.value)}
            />
            <List
              style={{
                display: 'flex',
                flexDirection: 'column',
                maxHeight: '40vh',
                overflow: 'auto',
                overscrollBehavior: 'contain'
              }}>
              {results.map((friend) => {
                return (
                  <ListItem key={friend.id} disableGutters>
                    <ListItemButton onClick={() => handleResultClick(friend.id)}>
                      <ListItemText primary={friend.username} fontSize={12} />
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </List>
          </DialogContent>
          <DialogActions>
            <Button variant="outlined" onClick={() => setOpen(false)}>
              Cancel
            </Button>
          </DialogActions>
        </>
      }
    />
  );
}

AddMemberForumDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  setOpen: PropTypes.func.isRequired
};

export default ActivityBar;
