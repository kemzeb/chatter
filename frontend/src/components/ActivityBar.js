import { useLocation } from 'react-router-dom';
import Box from '@mui/material/Box';
import GroupIcon from '@mui/icons-material/Group';
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

function ActivityBar() {
  const location = useLocation();
  const [path, setPath] = useState(null);

  useEffect(() => {
    setPath(location.pathname);
  }, [location]);

  return (
    <>
      <Box
        style={{
          height: '48px',
          display: 'flex',
          alignItems: 'center',
          padding: '8px',
          backgroundColor: '#424549'
        }}>
        {path === '/dashboard' && <FriendSpecificBar />}
      </Box>
    </>
  );
}

export default ActivityBar;
