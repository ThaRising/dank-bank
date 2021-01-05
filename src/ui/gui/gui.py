import sys
import threading
import tkinter as tk
from typing import Optional

from rx.subject import Subject

from src.models import Kunde
from src.storage.exc import ObjectAlreadyExists
from .state import HistoryManager
from .widgets import DateEntry
from ..base import UI


class GUI(UI):
    window: Optional["GUIWindow"]
    main_view: Optional[tk.Frame]

    def __init__(self):
        self.storage = None
        self.history = HistoryManager(self)

        self.master = None
        self.toolbar = None
        self.main_view = None
        self.current_menu = None

        self.select_storage()

        if not self.storage:
            sys.exit(0)

        super(GUI, self).__init__(self.storage)
        self.storage.db.create()

        # Unfortunately Pythons RX is nothing like RxJs
        # so this does not work as intended
        # TODO refactor to AsyncSubject to run in emulated event-loop?
        # This could solve the subscriber distribution issues
        self.tasks = Subject()

        # TODO wtf is this even supposed to be
        # Galaxy brain thread management
        self.threads = [threading.Thread(target=self.data_binding)]
        for thread in self.threads:
            thread.start()

        self.window = GUIWindow(self)

    def cleanup(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.destroy()
        sys.exit(0)

    def select_storage(self):
        storage_choice_window = tk.Tk()
        storage_choice_window.title("Speichertyp auswählen")

        # Labels
        title = tk.Label(
            storage_choice_window,
            text="Wilkommen bei der Dank Bank",
            font=("Calibri", 14),
        )
        title.grid(row=0, sticky=tk.N, pady=10)

        question = tk.Label(
            storage_choice_window,
            text="Welche Datenhaltung wollen sie verwenden?",
            font=("Calibri", 12),
        )
        question.grid(row=2, sticky=tk.N)

        def set_storage(store) -> None:
            self.storage = store()
            storage_choice_window.destroy()

        # Buttons
        for i, (s_type, storage) in enumerate(self.storage_types.items()):
            tk.Button(
                storage_choice_window,
                text=s_type.upper(),
                font=("Calibri", 12),
                width=20,
                command=lambda *a, **kw: set_storage(storage),
            ).grid(row=5 + i, sticky=tk.N, pady=10)

        storage_choice_window.mainloop()

    def mainloop(self):
        self.current_menu = UserMenu(self)
        self.history.forward_switch_menu(to_fn=self.current_menu.main_menu)

        self.window.mainloop()

    def clear_main_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # irredeemable code, but there will have to be some fallback mgmt later
    """
    def context_window(self):
        if not self.user:
            self.clear_main_view()
            UserMenu(self).main_menu()
    """

    def data_binding(self):
        """ Attempt to emulate Angulars two-way data binding. """
        # TODO rework this code to work with Subjects
        while True:
            if not self.tasks.empty():
                task = self.tasks.get()
                task(self)


class GUIWindow(tk.Tk):
    toolbar: "Toolbar"
    main_view: tk.Frame

    def __init__(self, state: GUI, *args, **kwargs) -> None:
        self.state = state

        super(GUIWindow, self).__init__(*args, **kwargs)

        self.protocol("WM_DELETE_WINDOW", self.state.cleanup)
        self.title("Dank Bank GUI v1.0")
        self.geometry("1280x720")

        self.toolbar = Toolbar(self, self.state)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.main_view = tk.Frame(self)
        self.main_view.pack()

        self.error_msg = tk.Label(self)
        self.error_msg.pack()

    # TODO all of this is garbage
    @property
    def error(self):
        return self.error_msg

    @error.setter
    def error(self, e):
        self.error_msg.configure(text=e)

    @error.deleter
    def error(self):
        self.error_msg.configure(text="")


class Toolbar(tk.Frame):
    def __init__(self, root, state: GUI, *args, **kwargs) -> None:
        self.state = state
        super(Toolbar, self).__init__(root, *args, **kwargs)

        # User Actions
        self.user_actions = tk.Frame(self)
        self.user_logout_button = tk.Button(self.user_actions, text="Logout")
        self.user_logout_button.pack(side=tk.LEFT)
        self.user_label = tk.Label(self.user_actions, text="Eingeloggt als ?")
        self.user_label.pack(side=tk.RIGHT)

        # Konto Actions
        # TODO Try tk.Variable() trace_binding for widget updates
        self.konto_actions = tk.Frame(self)
        self.konto_logout_button = tk.Button(self.konto_actions, text="Konto wechseln")
        self.konto_logout_button.pack(side=tk.LEFT)
        self.konto_label = tk.Label(self.konto_actions, text="Konto ?")
        self.konto_label.pack(side=tk.RIGHT)

        # Back Button
        self.back_button = tk.Button(
            self, text="Zurück", command=self.state.history.backward_switch_menu
        )

        self.back_button.pack()


class UserMenu:
    def __init__(self, master: GUI) -> None:
        self.master = master
        self.view = master.main_view
        self.history = master.history

        self.error_field = None
        self.user = None

    def main_menu(self):
        heading = tk.Label(self.view, text="Nutzerauswahl")
        heading.pack()

        actions = [
            (
                "Login",
                lambda: (
                    self.history.forward_switch_menu(
                        current_fn=self.main_menu, to_fn=self.login_menu
                    )
                ),
            ),
            (
                "Registrieren",
                lambda: (
                    self.history.forward_switch_menu(
                        current_fn=self.main_menu, to_fn=self.create_menu
                    )
                ),
            ),
            (
                "Kundenaccount Löschen",
                lambda: (
                    self.history.forward_switch_menu(
                        current_fn=self.main_menu, to_fn=self.delete_menu
                    )
                ),
            ),
        ]

        for text, action in actions:
            tk.Button(self.view, text=text, command=action).pack()

    def login_menu(self, action=None):
        if not action:
            action = self.login_action

        heading = tk.Label(self.view, text="Nutzerauswahl")
        heading.pack()

        input_fields = [("Username", {}), ("Password", {"show": "*"})]
        entries = []

        for text, options in input_fields:
            tk.Label(self.view, text=text).pack()

            entry = tk.Entry(self.view, **options)
            entry.pack()
            entries.append(entry)

        def login():
            return action(*[e.get() for e in entries])

        tk.Button(self.view, text="Login", command=login).pack()

        self.error_field = tk.Label(self.view)
        self.error_field.pack()

    def login_action(self, username: str, password: str) -> None:
        user = Kunde.objects.login_user(username, password)

        if not user:
            self.master.window.error = "meh"
        else:
            self.user = user
            # self.master.tasks.put()

    def delete_action(self, username: str, password: str) -> None:
        user = Kunde.objects.login_user(username, password)

        if not user:
            self.error_field.config(text="meh")
        else:
            user.objects.delete()

    def create_menu(self):
        heading = tk.Label(self.view, text="Nutzerauswahl")
        heading.pack()

        input_fields = {
            "name": ("Name", {}),
            "strasse": ("Strasse", {}),
            "stadt": ("Stadt", {}),
            "plz": ("PLZ", {}),
            "geb_date": ("Geburtsdatum (dd mm yyyy)", {"cls": DateEntry}),
            "username": ("Username", {}),
            "password": ("Password", {"show": "*"}),
        }
        entries = {}

        for field, (label_text, options) in input_fields.items():
            tk.Label(self.view, text=label_text).pack()

            if "cls" in options:
                entry_cls = options.pop("cls")
            else:
                entry_cls = tk.Entry

            entry = entry_cls(self.view, **options)
            entry.pack()
            entries[field] = entry

        def create():
            return self.create_action({k: v.get() for k, v in entries.items()})

        tk.Button(self.view, text="Nutzer erstellen", command=create).pack()

        self.error_field = tk.Label(self.view)
        self.error_field.pack()

    def create_action(self, data):
        errors = []

        try:
            kunde = Kunde(**data)
            kunde.objects.save()

        # Hollow would be sad about this code
        except AssertionError as exc:
            errors.append(exc.args[0])
        except ObjectAlreadyExists:
            self.error_field.config(
                text=f"Kunde mit Nutzername {kunde.username} existiert bereits."
            )
        else:
            self.master.user = kunde
            # TODO debounce this by at least 100ms, it runs way too often
            self.master.master.update_idletasks()

        finally:
            if errors:
                error_text = "\n".join(errors)
                self.error_field.config(text=error_text)

    def delete_menu(self):
        self.login_menu(action=self.delete_action)
        self.history.clear()
