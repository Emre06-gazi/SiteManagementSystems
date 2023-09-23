__all__ = ("run", )


def run():
    from project.modules import modules
    from gc import collect
    collect()

    @modules.socketio.on("connect", namespace="/base")
    def connect():
        ...
        # modules.socketio.emit("lastStatus", dumps(modules.registeredDevices.get(client_id, {})), namespace=f"/canvas/{client_id}")

    @modules.socketio.on("disconnect", namespace="/base")
    def disconnect():
        ...


    modules.system.start()
