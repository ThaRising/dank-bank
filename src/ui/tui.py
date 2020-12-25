from datetime import date
from getpass import getpass
from typing import Optional, Callable, ClassVar

from src.storage import Storage
from src.storage.exc import ObjectAlreadyExists, ObjectNotFound
from src.models.konto import Konto
from src.models import Kunde
from src.utils import IterableKeyDictionary
from .base import UI


class TUI(UI):
    yes_no_answer_choices: ClassVar[dict] = IterableKeyDictionary({
        ("J", "j", "Y", "y"): True,
        ("N", "n"): False
    })

    def __init__(self, storage: Optional[Storage] = None) -> None:
        super().__init__(storage)

        if not storage:
            # Let the user select their storage type
            while True:
                print("Bitte wählen sie ihren Speichertypen.")
                storage_type = input(
                    "JSON oder SQL? "
                )

                try:
                    storage = self.storage_types[
                        storage_type.lower()
                    ]()
                    self.storage = storage
                except KeyError:
                    print("Üngültige Eingabe!")
                    print(f"Kein verfügbarer Speichertyp: '{storage_type}'.\n")
                else:
                    break
        else:
            # Use the storage that the user supplied as a parameter
            self.storage = storage
            print(f"{self.storage.manager.db_type.upper()} Datenspeicher wird genutzt.\n")

        self.storage.db.create()

    def yes_or_no_question(self, text: Optional[str] = "J / N: ") -> bool:
        """ Ask the user a simple Yes or No question """
        while True:
            choice = input(text)

            try:
                return self.yes_no_answer_choices[choice]

            except KeyError:
                print(f"Ungültige Auswahl '{choice}'.")
                print("Bitte erneut eingeben.")
                continue

    def mainloop(self):
        while True:
            # Select new or existing Kunde
            print("Haben sie bereits einen Account?")
            if self.yes_or_no_question():
                self.user = self.login_user()

            else:
                self.user = self.create_account()

            # Select new or existing Konto
            if not self.user.konten:
                # If the user does not have a bank account yet
                # we create a default one automatically
                konto = Konto(
                    besitzer=self.user.pk
                )
                konto.objects.save()

            # Display all the bank accounts the user has
            # As well as their balance and account-id
            print(f"\nWillkommen {self.user.name}!")
            print("Ihre Konten:")
            self.show_konten(self.user.konten)

            while not (konto := self.choose_bank_account()):
                continue

            self.konto = konto
            print(f"Konto: '{self.konto.kontonummer}', wurde gewählt.")

            while True:
                self.perform_actions()
                print("Möchten sie eine weitere Aktion ausführen?")
                print("Andernfalls wird das Programm beendet.")

                if self.yes_or_no_question(text="Fortfahren (J) / Abbrechen (N): "):
                    print(
                        "Wollen sie mit dem aktuellen Kunde und Konto fortfahren?"
                    )
                    if self.yes_or_no_question():
                        continue

                    else:
                        return self.mainloop()

                else:
                    return

    def show_konten(self, konten: list) -> None:
        if not konten:
            print("Es sind keine Konten verfügbar.")
            return

        for i, konto in enumerate(konten):
            print(f"{i + 1}. {konto.kontonummer}:")
            print(
                f"Kontostand: {self._format_balance(konto.kontostand)}\n"
            )

    def choose_bank_account(self) -> Optional[Konto]:
        # Now let the user choose their account,
        # either by account-id or the numeric index of the listing
        selection = input(
            "Bitte wählen sie ein Konto aus der Liste: "
        )

        try:
            # Check if the user provided a numeric index
            selection = int(selection)

            if selection <= 0:
                raise IndexError

            return self.user.konten[selection - 1]

        except ValueError:
            # the user provided an account-id
            for konto in self.user.konten:
                if getattr(konto, "kontonummer") == selection:
                    return konto

        except IndexError:
            # An integer was provided but it didnt fit an index
            # in the users bank account list
            print(f"Kein verfügbares Konto an der Stelle {selection}.")

        return None

    def create_account(self) -> Kunde:
        kundendaten= {}  # noqa dict literal

        while True:
            if not kundendaten:
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

            kundendaten["username"] = input("Username: ")
            kundendaten["password"] = Kunde.objects.hash_password(
                getpass("Passwort: ")
            )

            try:
                kunde = Kunde(**kundendaten)
                kunde.objects.save()
                break

            except ObjectAlreadyExists:
                print("Ein Nutzer mit dem gewählten Nutzername existiert bereits.")
                print("Wenn sie den Nutzernamen anpassen wollen, wählen sie jetzt 'J'.")
                print("Andernfalls können sie sich anmelden, wählen sie dafür 'N'.")

                if self.yes_or_no_question(text=""):
                    continue

                else:
                    return self.login_user()

        return kunde  # noqa ref before assignment

    def login_user(self) -> Kunde:
        while True:
            print("=====LOGIN=====")
            username = input("Username: ")
            password = getpass("Passwort: ")
            user = Kunde.objects.login_user(username, password)
            if user:
                return user
            print("Falsches Passwort oder Username.")

    def perform_actions(self):
        # Select action
        action = self.select_action()

        action()

        if action.__name__ != "_show_balance":
            self._show_balance()

    def select_action(self) -> Callable[[], None]:
        actions = IterableKeyDictionary({
            ("1", "einzahlen"): self._do_deposit,
            ("2", "auszahlen"): self._do_withdraw,
            ("3", "überweisung"): self._do_transfer,
            ("4", "kontostand"): self._show_balance,
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

    def _do_deposit(self) -> None:
        while True:
            print("Wie viel möchten Sie einzahlen?")

            try:
                einzahlung = input()
                einzahlung = self._format_deposit(einzahlung)
                break

            except ValueError as exc:
                print(exc.args[0])
                print("Bitte geben sie einen gültigen Wert ein.")
                continue

        self.do_deposit(einzahlung)  # noqa ref before assignment

    def _do_withdraw(self) -> None:
        while True:
            print("Wie viel möchten Sie abheben?")

            try:
                auszahlung = input()
                auszahlung = self._format_deposit(auszahlung)

                if auszahlung > self.konto.kontostand:
                    print(
                        "Sie können nicht mehr als den verfügbaren Saldo von "
                        f"{self.show_balance(self.konto)} "
                        "abheben."
                    )
                    continue

                break

            except ValueError as exc:
                print(exc.args[0])
                print("Bitte geben sie einen gültigen Wert ein.")
                continue

        self.do_withdraw(auszahlung)  # noqa ref before assignment

    def _do_transfer(self) -> None:
        print(
            "Sie können entweder auf eines ihrer eigenen Konten,\n"
            "oder auf das Konto einer anderen Person Geld überweisen.\n"
        )
        print("Eigenen Konten, welche als Ziel gelten können:")
        self.show_konten([
            k for k in self.user.konten if not k.kontonummer == self.konto.kontonummer
        ])

        while True:
            print("Bitte wählen sie ein Konto zu dem die Geld überweisen wollen.")
            kontonummer = input("Kontonummer: ")

            if kontonummer == self.konto.kontonummer:
                print("Sie können keine Überweisung auf das aktuell gewählte Konto machen.")
                print("Bitte erneut eingeben!")
                continue

            try:
                konto = Konto.objects.get(kontonummer)

            except ObjectNotFound:
                print("Kein Konto mit der angegebenen Kontonummer gefunden")
                print("Möchten sie den Prozess abbrechen oder ein anderes Konto wählen?")

                if self.yes_or_no_question(text="Abbrechen (J) / Weitermachen (N): "):
                    return

                else:
                    continue

            else:
                break

        print(
            f"Überweisung von '{self.konto.kontonummer}' -> '{konto.kontonummer}"  # noqa
        )
        print("Welche Summe wollen sie überweisen?")

        while True:
            try:
                summe = input()
                summe = self._format_deposit(summe)
                break

            except ValueError as exc:
                print(exc.args[0])
                print("Bitte geben sie einen gültigen Wert ein.")
                continue

        self.do_transfer(summe, konto, self.konto)

    def _show_balance(self) -> None:
        print("Der aktuelle Kontostand beträgt:")
        print(self.show_balance())


if __name__ == '__main__':
    TUI()
