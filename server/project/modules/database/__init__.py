__all__ = ("createDatabase",)


def createDatabase():
    from project.modules.database.database import Database

    Database()
