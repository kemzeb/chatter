import PropTypes from 'prop-types';
import {
  Avatar,
  Box,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import useAxiosProtected from '../utils/useAxiosProtected';
import { useCallback } from 'react';

function FriendList({ list, isPending }) {
  return (
    <List style={{ maxHeight: '78vh', overflowY: 'auto', overscrollBehavior: 'contain' }}>
      {list?.map((friend) => {
        return isPending ? (
          <PendingFriendListItem key={friend.id} request={friend} />
        ) : (
          <FriendListItem key={friend.id} friend={friend} />
        );
      })}
    </List>
  );
}

FriendList.propTypes = {
  list: PropTypes.array.isRequired,
  isPending: PropTypes.bool.isRequired
};

function FriendListItem({ friend }) {
  return (
    <ListItem disableGutters divider>
      <ListItemAvatar>
        <Avatar>{friend.username.charAt(0).toLowerCase()}</Avatar>
      </ListItemAvatar>
      <ListItemText primary={friend.username} />
      <IconButton>
        <MoreVertIcon color="primary" />
      </IconButton>
    </ListItem>
  );
}

FriendListItem.propTypes = {
  friend: PropTypes.shape({
    username: PropTypes.string.isRequired
  }).isRequired
};

function PendingFriendListItem({ request }) {
  const axios = useAxiosProtected();
  const handleReject = useCallback(() => {
    axios
      .delete(`/api/users/me/friendrequests/${request.id}/?accept=0`)
      .catch((error) => console.error('Unable to reject friend request', error));
  });
  const handleAccept = useCallback(() => {
    axios
      .delete(`/api/users/me/friendrequests/${request.id}/?accept=1`)
      .catch((error) => console.error('Unable to accept friend request', error));
  });

  return (
    <ListItem disableGutters divider>
      <ListItemAvatar>
        <Avatar>{request.requester.username.charAt(0).toLowerCase()}</Avatar>
      </ListItemAvatar>
      <ListItemText primary={request.requester.username} />
      <Box style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Button variant="outlined" onClick={handleReject}>
          <ListItemText color="text.primary" primary="Reject" />
        </Button>
        <Button variant="outlined" onClick={handleAccept}>
          <ListItemText color="text.primary" primary="Accept" />
        </Button>
      </Box>
    </ListItem>
  );
}

PendingFriendListItem.propTypes = {
  request: PropTypes.shape({
    id: PropTypes.number.isRequired,
    requester: PropTypes.shape({
      username: PropTypes.string.isRequired
    }).isRequired
  }).isRequired
};

export default FriendList;
