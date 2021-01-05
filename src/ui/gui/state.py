import queue
from typing import Callable, Optional


class HistoryManager:
    def __init__(self, master, fallback: Optional[Callable[[], None]] = None) -> None:
        self.master = master
        self.fallback = fallback

        self.history = queue.LifoQueue()

    def forward_switch_menu(self, to_fn, current_fn=None) -> None:
        if current_fn:
            self.history.put(current_fn)

        self.master.clear_main_view()

        to_fn()

    def backward_switch_menu(self) -> None:
        if self.history.empty():
            if self.fallback:
                self.fallback()

            return

        fn = self.history.get()
        self.master.clear_main_view()

        fn()

    def clear(self):
        del self.history
        self.history = queue.LifoQueue()
