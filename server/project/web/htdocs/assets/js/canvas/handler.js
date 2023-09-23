deviceSocket.on("connect", (client_id) => {
    serverConnected();
});

deviceSocket.on("disconnect", (client_id) => {
    serverDisconnected();
});

deviceSocket.on("deviceConnected", (client_id) => {
    onConnected(client_id);
});

deviceSocket.on("lastStatus", (packet) => {
    lastStatus(packet);
});

deviceSocket.on("deviceReceived", (packet) => {
    onMessage(packet);
});

deviceSocket.on("deviceDisconnected", (client_id) => {
    onDisconnected(client_id);
});

