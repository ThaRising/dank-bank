from datetime import date
from tkinter import *
import sys
from src.models import Kunde
from src.models.konto import Konto
from src.storage import Storage
from src.storage.exc import ObjectAlreadyExists, ObjectNotFound
from drizm_commons.utils.type import IterableKeyDictionary
from .base import UI



class GUI(UI):
    def __init__(self):
        self.storage = None
        self.login_window = None

        self.tmpNamen = None
        self.tmpAnschrift = None
        self.tmpStadt = None
        self.tmpPLZ = None
        self.tmpGdatum = None
        self.tmpUsername = None
        self.tmpPasswort = None
        self.tmpUsernameL = None
        self.tmpPasswortL = None

        self.master = Tk()
        self.master.title("Speichertyp wählen")

        # Labels
        Label(
            self.master, text="Wilkommen bei der Dank Bank", font=("Calibri", 14)
        ).grid(row=0, sticky=N, pady=10)
        Label(
            self.master,
            text="In dieser App können sie ihr Konto verwalten",
            font=("Calibri", 12),
        ).grid(row=1, sticky=N)
        Label(
            self.master,
            text="Welche Datenhaltung wollen sie verwenden?",
            font=("Calibri", 12),
        ).grid(row=2, sticky=N)

        # Buttons
        Button(
            self.master,
            text="SQL",
            font=("Calibri", 12),
            width=20,
            command=self.login_sql,
        ).grid(row=5, sticky=N, pady=10)
        Button(
            self.master,
            text="JSON",
            font=("Calibri", 12),
            width=20,
            command=self.login_json,
        ).grid(row=6, sticky=N, pady=10)
        self.master.mainloop()

        super().__init__(self.storage)

    def mainloop(self):
        self.master = Tk()
        self.master.title("Banking App")
        self.master.attributes("-alpha", 0.0)
        self.master.geometry("0x0")
        self.master.iconify()

        self.login_window = Toplevel(self.master)
        self.login_window.title("Login")
        self.create_login_window()

        self.master.mainloop()

    def create_login_window(self):
        # Labels
        Label(
            self.login_window, text="Wilkommen bei der Dank Bank", font=("Calibri", 14)
        ).grid(
            row=0,
            sticky=N,
        )
        Label(
            self.login_window, text="Was möchten sie tun?", font=("Calibri", 12)
        ).grid(row=1, sticky=W, pady=10)

        # Buttons
        Button(
            self.login_window, text="Login", command=self.login, font=("Calibri", 12)
        ).grid(row=2, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Nutzer erstellen",
            command=self.createUser,
            font=("Calibri", 12),
        ).grid(row=3, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Bestehenden Nutzer löschen",
            command=self.deleteUser,
            font=("Calibri", 12),
        ).grid(row=4, sticky=N, pady=5)

    def create_main_window(self):
        # Labels
        Label(
            self.login_window, text="Sie sind Angemeldet", font=("Calibri", 12)
        ).grid(
            row=0,
            sticky=N,
        )
        Label(
            self.login_window, text="Was möchten sie tun?", font=("Calibri", 12)
        ).grid(row=1, sticky=W, pady=10)

        # Buttons
        Button(
            self.login_window, text="Einzahlung", font=("Calibri", 12)
        ).grid(row=2, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Auszahlung",
            font=("Calibri", 12),
        ).grid(row=3, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Überweisung tätigen",
            font=("Calibri", 12),
        ).grid(row=4, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Kontostand",
            font=("Calibri", 12),
        ).grid(row=5, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Abmelden",
            command=self.backloginwindow,
            font=("Calibri", 12),
        ).grid(row=6, sticky=N, pady=5)

    def create_konto_window(self):
        # Labels
        Label(
            self.login_window, text="Dank Bank", font=("Calibri", 12)
        ).grid(
            row=0,
            sticky=N,
        )
        Label(
            self.login_window, text="Bitte wählen sie eine Aktion?", font=("Calibri", 12)
        ).grid(row=1, sticky=W, pady=10)

        # Buttons
        Button(
            self.login_window, text="Neues Konto eröffnen", command=self.konto_create, font=("Calibri", 12)
        ).grid(row=2, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Bestehendes Konto auswählen",
            font=("Calibri", 12),
        ).grid(row=3, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Bestehendes Konto löschen",
            font=("Calibri", 12),
        ).grid(row=4, sticky=N, pady=5)
        Button(
            self.login_window,
            text="Abmelden",
            command=self.backloginwindow,
            font=("Calibri", 12),
        ).grid(row=5, sticky=N, pady=5)

    def login_sql(self):
        self.storage = self.storage_types["sql"]()
        self.master.destroy()
        self.storage.db.create()

    def login_json(self):
        self.storage = self.storage_types["json"]()
        self.master.destroy()
        self.storage.db.create()

    def login(self):
        self.login_window.destroy()
        self.login_window = Toplevel(self.master)
        self.login_window.title("Login")

        self.tmpUsernameL = StringVar()
        self.tmpPasswortL = StringVar()

        # Labels
        Label(self.login_window, text="Bitte Anmelden", font=("Calibri", 12)).grid(
            row=0, sticky=N, pady=10
        )
        Label(self.login_window, text="Username", font=("Calibri", 12)).grid(
            row=1, sticky=W
        )
        Label(self.login_window, text="Passwort", font=("Calibri", 12)).grid(
            row=2, sticky=W
        )

        # Entry
        Entry(
            self.login_window, textvariable=self.tmpUsernameL
        ).grid(row=1, column=1, padx=5)
        Entry(self.login_window, textvariable=self.tmpPasswortL, show="*").grid(row=2, column=1, padx=5)

        # Button
        Button(self.login_window, text="Login", width=15, command=self.buttonLogin, font=("Calibri", 12)).grid(
            row=3, sticky=W, pady=5, padx=5
        )
        Button(self.login_window, text="Zurück", width=15,command=self.backloginwindow, font=("Calibri", 12)).grid(
            row=4, sticky=W, pady=5, padx=5
        )

    def buttonLogin(self) -> Kunde:
        user = Kunde.objects.login_user(self.tmpUsernameL.get(), self.tmpPasswortL.get())
        if not user:
            self.login_window.destroy()
            self.login_window = Toplevel(self.master)
            self.login_window.title("Fehler")

            # Labels
            Label(
                self.login_window, text="Benutzer nicht vorhanden", font=("Calibri", 14)
            ).grid(row=0, sticky=N, pady=10)
            Label(
                self.login_window, text="Bitte einen Benutzer angelegen oder erneut versuchen", font=("Calibri", 12)
            ).grid(row=1, sticky=N, pady=10)

            # Buttons
            Button(
                self.login_window,
                text="Zurück",
                width=15,
                font=("Calibri", 12),
                command=self.backloginwindow,
            ).grid(row=2, sticky=W, pady=5, padx=5)
        self.user_actions()

    def createUser(self):
        self.login_window.destroy()
        self.login_window = Toplevel(self.master)
        self.login_window.title("Benutzer erstellen")

        self.tmpNamen = StringVar()
        self.tmpAnschrift = StringVar()
        self.tmpStadt = StringVar()
        self.tmpPLZ = StringVar()
        self.tmpGdatum = StringVar()
        self.tmpUsername = StringVar()
        self.tmpPasswort = StringVar()

        # Labels
        Label(
            self.login_window, text="Bitte Daten eintragen", font=("Calibri", 12)
        ).grid(row=0, sticky=N, pady=10)
        Label(self.login_window, text="Vor und Nachnamen", font=("Calibri", 12)).grid(
            row=1, sticky=W
        )
        Label(
            self.login_window, text="Straße und Hausnummer", font=("Calibri", 12)
        ).grid(row=2, sticky=W)
        Label(self.login_window, text="Stadt", font=("Calibri", 12)).grid(
            row=3, sticky=W
        )
        Label(self.login_window, text="Postleitzahl", font=("Calibri", 12)).grid(
            row=4, sticky=W
        )
        Label(self.login_window, text="Geburtsdatum(dd mm yyyy)", font=("Calibri", 12)).grid(
            row=5, sticky=W
        )
        Label(self.login_window, text="Username(min. 5 Buchstaben", font=("Calibri", 12)).grid(
            row=6, sticky=W
        )
        Label(self.login_window, text="Passwort", font=("Calibri", 12)).grid(
            row=7, sticky=W
        )

        # Entry
        Entry(self.login_window, textvariable=self.tmpNamen).grid(
            row=1, column=1, padx=5
        )
        Entry(self.login_window, textvariable=self.tmpAnschrift).grid(
            row=2, column=1, padx=5
        )
        Entry(self.login_window, textvariable=self.tmpStadt).grid(
            row=3, column=1, padx=5
        )
        Entry(self.login_window, textvariable=self.tmpPLZ).grid(row=4, column=1, padx=5)
        Entry(self.login_window, textvariable=self.tmpGdatum).grid(
            row=5, column=1, padx=5
        )
        Entry(self.login_window, textvariable=self.tmpUsername).grid(
            row=6, column=1, padx=5
        )
        Entry(self.login_window, textvariable=self.tmpPasswort, show="*").grid(
            row=7,
            column=1,
            padx=5,
        )

        # Button
        Button(
            self.login_window,
            text="Erstellen",
            width=15,
            font=("Calibri", 12),
            command=self.buttonCreate,
        ).grid(row=8, sticky=W, pady=5, padx=5)
        Button(self.login_window, text="Zurück", width=15, command=self.backloginwindow, font=("Calibri", 12)).grid(
            row=9, sticky=W, pady=5, padx=5
        )

    def buttonCreate(self) -> Kunde:
        kundendaten = {}  # noqa dict literal
        kundendaten["name"] = self.tmpNamen.get()
        kundendaten["strasse"] = self.tmpAnschrift.get()
        kundendaten["stadt"] = self.tmpStadt.get()
        kundendaten["plz"] = self.tmpPLZ.get()

        d, m, y = [int(i) for i in self.tmpGdatum.get().split()]
        kundendaten["geb_date"] = date(day=d, month=m, year=y)

        kundendaten["username"] = self.tmpUsername.get()
        kundendaten["password"] = Kunde.objects.hash_password(self.tmpPasswort.get())

        try:
            kunde = Kunde(**kundendaten)
            kunde.objects.save()
            return kunde

        except ObjectAlreadyExists:
            self.login_window.destroy()
            self.login_window = Toplevel(self.master)
            self.login_window.title("Fehler")
            Label(
                self.login_window, text="Nutzer existiert bereits", font=("Calibri", 12)
            ).grid(row=0, sticky=N, pady=10)
            Button(
                self.login_window,
                text="Zurück",
                width=15,
                font=("Calibri", 12),
                command=self.backloginwindow,
            ).grid(row=1, sticky=W, pady=5, padx=5)

        self.backloginwindow()

    def deleteUser(self):
        self.login_window.destroy()
        self.login_window = Toplevel(self.master)
        self.login_window.title("Benutzer löschen")

        # Labels
        Label(
            self.login_window, text="Leider noch keine Funktion", font=("Calibri", 12)
        ).grid(row=0, sticky=N, pady=10)

        # Buttons
        Button(
            self.login_window,
            text="Zurück",
            width=15,
            font=("Calibri", 12),
            command=self.backloginwindow,
        ).grid(row=1, sticky=W, pady=5, padx=5)

    def backloginwindow(self):
        self.login_window.destroy()
        self.login_window = Toplevel(self.master)
        self.login_window.title("Login")
        self.create_login_window()

    def konto_create(self) -> None:
        konto = Konto(besitzer=self.user.pk)
        konto.objects.save()
        print(true)


    def user_actions(self):
        self.login_window.destroy()
        self.login_window = Toplevel(self.master)
        self.login_window.title("Login")
        self.create_konto_window()

