import PropTypes from 'prop-types';
import { Avatar, IconButton, List, ListItem, ListItemAvatar, ListItemText } from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';

function FriendList({ list, isPending }) {
  return (
    <List style={{ maxHeight: '78vh', overflowY: 'auto', overscrollBehavior: 'contain' }}>
      {list?.map((friend) => {
        return isPending ? (
          <PendingFriendListItem key={friend.id} pendingFriend={friend} />
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

function PendingFriendListItem({ pendingFriend }) {
  return (
    <ListItem disableGutters divider>
      <ListItemAvatar>
        <Avatar>{pendingFriend.requester.username.charAt(0).toLowerCase()}</Avatar>
      </ListItemAvatar>
      <ListItemText primary={pendingFriend.requester.username} />
      <IconButton>
        <MoreVertIcon color="primary" />
      </IconButton>
    </ListItem>
  );
}

PendingFriendListItem.propTypes = {
  pendingFriend: PropTypes.shape({
    requester: PropTypes.shape({
      username: PropTypes.string.isRequired
    }).isRequired
  }).isRequired
};

export default FriendList;
