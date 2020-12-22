from src.storage import Storage
from getpass import getpass
from src.storage.models.kunde import Kunde
from src.storage.models.konto import Konto
from typing import Any, Optional, TypeVar, Callable
from datetime import date
import decimal

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
        # Select SQL or JSON
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
                self.storage.db.create()
            except KeyError:
                print("Falsche Eingabe!")
            else:
                break

        # Select new or existing Kunde
        while (p := input(
                "Haben Sie bereits einen Account J/N?: "
        )) not in ("j", "J", "n", "N"):
            print("Ungültige Eingabe.")

        if p.lower() == "j":
            self.user = self.login_user()
        else:
            self.user = self.create_account()

        # Select new or existing Konto
        if not self.user.konten:
            konto = Konto(
                besitzer=self.user.pk
            )
            konto.objects.save()

        for i, konto in enumerate(self.user.konten):
            print(f"{i + 1}. {konto.kontonummer}:")

            print(
                self._format_balance(konto.kontostand)
            )

        konto_index = input("Wähle dein Konto aus: ")
        self.konto = self.user.konten[int(konto_index) - 1]

        # Select action
        action = self.select_action()
        action()

    # noinspection PyMethodMayBeStatic
    def _format_balance(self, amount: int) -> str:
        balance = f"{amount!s:0>4}"
        balance = balance[:-2] + "." + balance[-2:]
        return f"{balance}€"

    def create_account(self) -> Kunde:
        kundendaten= {}  # noqa dict literal
        kundendaten["username"] = input("Username: ")
        kundendaten["password"] = Kunde.objects.hash_password(
            getpass("Passwort: ")
        )
        kundendaten["name"] = input("Vor und Nachname: ")
        kundendaten["strasse"] = input("Straße und Hausnummer: ")
        kundendaten["stadt"] = input("Stadt: ")
        kundendaten["plz"] = input("Postleitzahl: ")

        print("Bitte geben sie ihr Geburtsdatum ein.")
        print("Format: dd mm yyyy")
        geb_date = input()
        d, m, y = [int(i) for i in geb_date.split()]
        kundendaten["geb_date"] = date(
            day=d,
            month=m,
            year=y
        )

        kunde = Kunde(**kundendaten)
        kunde.objects.save()

        return kunde

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
        actions = Switch({
            ("1", "einzahlen"): self.do_deposit,
            ("2", "auszahlen"): self.do_withdraw,
            ("3", "überweisung"): self.do_transfer,
            ("4", "kontostand"): self.show_balance,
        })

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
        print(
            "Wie viel möchten Sie einzahlen?\n"
            "Die Zahl muss ein Integer sein."
        )
        einzahlung = input()

        for e in (".", ","):
            if e in einzahlung:
                num, dec = einzahlung.split(e)

                if len(dec) > 2:
                    raise ValueError

                einzahlung = einzahlung.replace(e, "")

        einzahlung = int(einzahlung) * 100
        self.konto.kontostand += einzahlung
        self.konto.objects.save()
        print(self.show_balance())

    def do_withdraw(self):
        pass

    def do_transfer(self):
        pass

    def show_balance(self):
        return self._format_balance(self.konto.kontostand)


if __name__ == '__main__':
    TUI()
