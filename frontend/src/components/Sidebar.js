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
import { getExampleChatGroups } from '../utils/examples';

function Sidebar() {
  const friendsText = 'Friends';
  const newChatGroupText = 'New Chat Group';
  const data = getExampleChatGroups();

  return (
    <Box
      sx={{
        flex: '0 0 16rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        bgcolor: '#36393f'
      }}>
      <Box sx={{ padding: '16px 16px 0px 16px ' }}>
        <List>
          <ListItem key={friendsText} disablePadding>
            <ListItemButton disableGutters>
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
        <List style={{ maxHeight: '78vh', overflowY: 'auto' }}>
          <ListItem key={-1} disablePadding>
            <ListItemText primaryTypographyProps={{ fontFamily: 'NotoSans' }}>
              CHAT GROUPS
            </ListItemText>
          </ListItem>
          {data.map((group) => {
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
          paddingLeft: '16px',
          paddingRight: '16px',
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
