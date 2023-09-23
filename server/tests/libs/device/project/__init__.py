__all__ = ("run",)


def run():
    while True:
        try:
            from project.libs import System
            system = System()
            system.start()

            from project.main import main
            main(system)

        except ImportError as E:
            print(E)
            import machine
            machine.reset()
        except KeyboardInterrupt:
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
