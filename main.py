from pywinauto import Desktop


def main():
    windows = Desktop(backend="uia").windows()
    for w in windows:
        print(w.window_text())
    return 0


main()

