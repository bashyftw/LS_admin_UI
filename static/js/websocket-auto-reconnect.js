/**
 * @file websocket-auto-reconnect.js
 * @brief JavaScript file to handle auto-reconnecting WebSockets.
 */

/**
 * @brief Function to initialize WebSocket connection and set up event handlers.
 * @param wsAddress The WebSocket address to connect to.
 * @return An object containing methods to interact with the WebSocket.
 */
export function setupWebSocket(wsAddress, onMessageHandler) {
  let ws = new WebSocket(wsAddress);

  const reconnect = () => {
    console.log("WebSocket closed. Attempting to reconnect...");
    ws = new WebSocket(wsAddress);
    setupEventHandlers();
  };

  const setupEventHandlers = () => {
    ws.onmessage = function(event) {
      onMessageHandler(event);  // Call the passed in function here
    };


    ws.onclose = function(event) {
      setTimeout(reconnect, 3000);  // Attempt to reconnect after 3 seconds
    };
  };

  setupEventHandlers();

  return {
    send: function(message) {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(message);
      } else {
        console.log(`WebSocket is not open. ReadyState: ${ws.readyState}`);
      }
    }
  };
}
