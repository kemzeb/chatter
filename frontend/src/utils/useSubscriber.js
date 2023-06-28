import { useCallback, useContext, useEffect, useRef } from 'react';
import AuthContext from './AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import jwtDecode from 'jwt-decode';

// TODO: Apparently the WebSocket API has an internal buffer that can store events
// while other events are being processed. We should question if such a buffer is
// scalable for a chat app.

function useSubscriber(onMessage) {
  const { getAuthTokens, storeAuthTokens, logoutUser } = useContext(AuthContext);
  const tokens = getAuthTokens();
  const webSocket = useRef(null);
  const url = useRef('ws://' + window.location.host + '/ws/chat?token=');
  const navigate = useNavigate();
  const handleIncomingMessage = useCallback((message) => {
    const data = JSON.parse(message.data);
    onMessage(data);
  });

  const setupConnection = useCallback((url) => {
    webSocket.current = new WebSocket(url);
    webSocket.current.onmessage = (event) => handleIncomingMessage(event);
  });

  const refreshAccessToken = useCallback(async () => {
    axios
      .post('/api/users/auth/login/refresh/', {
        refresh: tokens.refresh
      })
      .then((response) => {
        const newAccessToken = response.data.access;
        storeAuthTokens(newAccessToken, tokens.refresh);

        // Close the existing WebSocket connection.
        if (webSocket.current) {
          webSocket.current.close();
        }

        // Open a new WebSocket connection with the updated token.
        const newUrl = url.current + newAccessToken;
        setupConnection(newUrl);
      })
      .catch((error) => {
        console.error('Failed to refresh access token:', error);
        logoutUser();
        navigate('/');
      });
  });

  useEffect(() => {
    setupConnection(url.current + tokens.access);
    if (isTokenExpired(tokens.access)) {
      refreshAccessToken();
    }
    return () => {
      if (webSocket.current) {
        webSocket.current.close();
      }
    };
  }, []);
}

function isTokenExpired(token) {
  if (!token) return true;
  try {
    const decodedToken = jwtDecode(token);
    const expirationTime = decodedToken.exp;
    const currentTime = Date.now() / 1000; // Convert to seconds.
    return expirationTime <= currentTime;
  } catch (error) {
    console.error('Token decode failed:', error);
    return true;
  }
}

export default useSubscriber;
