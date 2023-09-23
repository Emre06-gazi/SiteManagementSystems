def _clearSystem(target="/", passHk=True):
    from uos import listdir, remove, rmdir

    for d in listdir(target):
        if d.startswith("boot") or (d.endswith(".hk") and passHk):
            continue
        try:
            _clearSystem(target + '/' + d)
        except OSError:
            remove(target + '/' + d)
    try:
        rmdir(target)
    except OSError:
        pass
_clearSystem()