from json import dumps

from flask import session, redirect, url_for
from math import inf


def login_required(_level=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if session.get("id", None):
                _userLevel = session.get("level", inf)

                if _userLevel == 0:
                    return func(*args, **kwargs)

                if _level:
                    if _level >= _userLevel:
                        return func(*args, **kwargs)
                    return dumps(dict(deined="İzinsiz giriş sayfası"))

                return func(*args, **kwargs)

            else:
                return redirect(url_for('login'))
        return wrapper
    return decorator
