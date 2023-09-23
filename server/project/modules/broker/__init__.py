__all__ = ("createBroker",)


def createBroker():
    from project.modules.broker.broker import Broker

    Broker()

