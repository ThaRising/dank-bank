from src.storage import Storage
from getpass import getpass
from src.storage.models.kunde import Kunde
from src.storage.models.konto import Konto
from typing import Any, Optional, TypeVar, Callable
from datetime import datetime

DictItem = TypeVar("DictItem")


class Switch(dict):
    __slots__ = ["__weakref__"]
    __doc__ = ""

    def __getitem__(self, item) -> Optional[DictItem]:
        for k in [k for k in self.keys() if type(k) is tuple or list]:
            if item in k:
                return super(Switch, self).__getitem__(k)
        return False


class TUI:
    storage: Storage
    user: Kunde
    balance: Konto

    def __init__(self) -> None:
        storage_types = {
            "sql": lambda: Storage("sql"),
            "json": lambda: Storage("json")
        }

        while True:
            storage_type = input(
                "Was willst du haben? JSON oder SQL? "
            )

            try:
                storage = storage_types[
                    storage_type.lower()
                ]()
                self.storage = storage
            except KeyError:
                print("Falsche Eingabe!")
            else:
                break

        self.user = self.login_user()

        action = self.select_action()
        action()

    def create_account(self) -> Kunde:
        # Still needs some validation
        # Check if User has account
        # if not he needs to input credentials
        new_account = input("Haben Sie bereits einen Account J/N?: ")
        if new_account.lower() == "j":
            while True:
                kundendaten= {}
                kundendaten["username"] = input("Username: ")
                kundendaten["password"] = getpass("Passwort: ")
                kundendaten["name"] = input("Vor und Nachname: ")
                kundendaten["strasse"] = input("Straße und Hausnummer: ")
                kundendaten["stadt"] = input("Stadt: ")
                kundendaten["plz"] = input("Postleitzahl: ")
                kundendaten["geb_date"] = input(datetime.date())
                kunde = Kunde(**kundendaten)
                kunde.objects.save()
                return kunde
        else:
            continue
    def login_user(self) -> Kunde:
        while True:
            print("=====LOGIN=====")
            username = input("Username: ")
            password = getpass("Passwort: ")
            user = Kunde.objects.login_user(username, password)
            if user:
                return user
            print("Falsches Passwort oder Username.")

    def select_action(self) -> Callable:
        actions = {
            ("1", "einzahlen"): self.do_deposit,
            ("2", "auszahlen"): self.do_withdraw,
            ("3", "überweisung"): self.do_transfer,
            ("4", "kontostand"): self.show_balance,
        }

        while True:
            print("Was wollen sie tun?")
            [
                print(
                    f"{num}. {action.capitalize()}"
                ) for num, action in actions.keys()
            ]
            action = input()
            try:
                action_to_execute = actions[action.lower()]
            except KeyError:
                print("Ungültige Option, bitte erneut eingeben.")
            else:
                return action_to_execute

    def do_deposit(self) -> Konto:
        while i == 1:
            print("Wie viel möchten Sie einzahlen? Die Zahl muss ein Integer sein.")
            einzahlung = int(input())
            balance = Konto.kontostand
            try:
                new_balance = balance + einzahlung
            except ValueError:
                print("Eingabe muss eine Integer sein")
            else:
                print("Der neue Kontostand ist: "new_balance"€")
                return new_balance
            i = input("0 um die Einzahlung zu beenden\n "
                      "1 für eine weitere Einzahlung")
            if i == 0:
                break
            elif i == 1:
                continue
            else:
                print("Es muss entweder ")



    def do_withdraw(self):
        pass

    def do_transfer(self):
        pass

    def show_balance(self):
        pass
