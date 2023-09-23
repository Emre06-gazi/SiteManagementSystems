if __name__ == "__main__":
    while True:
        try:
            from project import run

            run()
        except KeyboardInterrupt:
            continue
        break
