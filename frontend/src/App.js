import { Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { AuthProvider } from './utils/AuthContext';
import Friends from './components/Friends';
import ChatGroup from './components/ChatGroup';
import RequireAuth from './utils/RequireAuth';
import NotFound from './pages/NotFound';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import PendingFriends from './components/PendingFriends';

const theme = createTheme({
  typography: {
    fontFamily: ['Roboto', 'NotoSans', 'sans-serif'].join(',')
  },
  palette: {
    // TODO: Support light/dark theme globally!
    mode: 'dark',
    primary: {
      main: '#00b4ff'
    },
    secondary: {
      main: '#36393f'
    }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <Dashboard />
              </RequireAuth>
            }>
            <Route index element={<Friends />} />
            <Route path="chats/:id" element={<ChatGroup />} />
            <Route path="pending" element={<PendingFriends />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
