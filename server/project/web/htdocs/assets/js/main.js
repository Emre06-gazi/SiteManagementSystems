const socket_base = io.connect(`${server_ip}/base`, {
        pingInterval: 10000,
        pingTimeout: 60000
});



socket_base.on("connect", () => {
        console.log("Servere bağlanıldı")
});

socket_base.on("disconnect", () => {
        console.log("Serverden bağlantı koptu")
});

