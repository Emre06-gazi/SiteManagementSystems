__all__ = ("run",)


def run():
    while True:
        try:
            from project.libs import System
            from gc import collect
            system = System()
            system.start()
            collect()

            from project.main import main
            main(system)

        except ImportError as E:
            print(E)
            from machine import reset
            reset()
        except KeyboardInterrupt:
            try:
                system.shutdown()
            except (NameError, AttributeError, KeyError):
                pass
            while True:
                try:
                    pw = input("Quit Password -> ")
                    if not pw:
                        continue
                    break
                except (KeyboardInterrupt, EOFError):
                    print()
                    pass
            if pw == "brank":
                break
        finally:
            try:
                system.shutdown()
            except (NameError, AttributeError, KeyError):
                pass
            else:
                del system
            from gc import collect

            collect()
