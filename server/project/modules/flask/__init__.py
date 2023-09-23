__all__ = ("createApp",)


def createApp():
    from sys import modules
    from project.modules.flask.flask import myFlask as Flask

    cli = modules["flask.cli"]
    cli.show_server_banner = lambda *x: None

    Flask()
