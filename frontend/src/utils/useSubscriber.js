import { useCallback, useEffect, useRef } from 'react';

// FIXME: Handle WebSocket rejection when JWT auth has expired.

function useSubscriber(webSocketUrl, onMessage) {
  // TODO: Apparently the WebSocket API has an internal buffer that can store events
  // while other events are being processed. We should question if such a buffer is
  // scalable for a chat app.
  const socket = useRef();
  const handleIncomingMessage = useCallback((message) => {
    const data = JSON.parse(message.data);
    onMessage(data);
  });

  useEffect(() => {
    socket.current = new WebSocket(webSocketUrl);
    socket.current.addEventListener('message', handleIncomingMessage);
    return () => {
      socket.current.removeEventListener('message', handleIncomingMessage);
      socket.current.close();
    };
  }, []);
}

export default useSubscriber;
