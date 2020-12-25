from src.ui import TUI
from src.storage import Storage


if __name__ == '__main__':
    storage = Storage("sql")
    tui = TUI(storage)
    tui.mainloop()
