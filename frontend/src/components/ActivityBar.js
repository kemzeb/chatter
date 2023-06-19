import { useLocation } from 'react-router-dom';
import Box from '@mui/material/Box';
import GroupIcon from '@mui/icons-material/Group';
import ForumIcon from '@mui/icons-material/Forum';
import Typography from '@mui/material/Typography';
import { useEffect, useState } from 'react';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';

function FriendSpecificBar() {
  return (
    <Box style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <GroupIcon color="primary" />
      <Typography>Friends</Typography>
      <Divider flexItem orientation="vertical" />
      <Button variant="outlined">
        <Typography color="text.primary">Add Friend</Typography>
      </Button>
    </Box>
  );
}

function ChatGroupSpecificBar() {
  return (
    <Box style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <ForumIcon color="primary" />
      <Typography>Chat Group</Typography>
    </Box>
  );
}

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

export default ActivityBar;
