import atexit
from datetime import date
from getpass import getpass
from typing import Optional, Callable, ClassVar, List, Tuple, Any

from colorama import init, Fore, Style
import colorama

from src.models import Kunde
from src.models.konto import Konto
from src.storage import Storage
from src.storage.exc import ObjectAlreadyExists, ObjectNotFound
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
                print(Fore.LIGHTGREEN_EX + "Bitte wählen sie ihren Speichertypen.")
                storage_type = input(
                    "JSON oder SQL? "
                )

                try:
                    storage = self.storage_types[
                        storage_type.lower()
                    ]()
                    self.storage = storage
                except KeyError:
                    print(Fore.LIGHTRED_EX + "\nÜngültige Eingabe!")
                    print(Fore.LIGHTRED_EX + f"Kein verfügbarer Speichertyp: '{storage_type}'.\n")
                else:
                    break
        else:
            # Use the storage that the user supplied as a parameter
            self.storage = storage

        print(f"\n{self.storage.manager.db_type.upper()} Datenspeicher wird genutzt.\n")
        self.storage.db.create()
        colorama.init(autoreset=True)
        atexit.register(self.cleanup)

    # noinspection PyMethodMayBeStatic
    def cleanup(self) -> None:
        colorama.init()


    def mainloop(self):
        while True:
            # Select new or existing Kunde
            while not self.user:
                self.user_actions()

            print(Fore.LIGHTGREEN_EX + f"\nWillkommen, {self.user.name.strip()}!\n")

            # If the user does not have a bank account yet
            # we create a default one automatically
            if not self.user.konten:
                print(Fore.LIGHTRED_EX + "Es scheint so als haben sie bisher noch kein Konto bei uns.")
                print(Fore.LIGHTGREEN_EX + "Wir haben ihnen automatisch eines eröffnet!\n")

                konto = Konto(
                    besitzer=self.user.pk
                )
                konto.objects.save()

            while not self.konto:
                self.konto_selection_actions()

            print(Fore.LIGHTGREEN_EX + f"\nKonto: '{self.konto.kontonummer}', wurde gewählt.")

            while True:
                self.perform_actions()

                print("Möchten sie eine weitere Aktion ausführen?\n")
                print(Fore.LIGHTRED_EX + "Andernfalls wird das Programm beendet.")

                if self.yes_or_no_question(text="Fortfahren (J) / Abbrechen (N): "):
                    print("Wollen sie mit dem aktuellen Kunden fortfahren?")

                    if self.yes_or_no_question():
                        print("Wollen sie mit dem aktuellen Konto fortfahren?")

                        if self.yes_or_no_question():
                            continue

                        else:
                            self.konto = None
                            return self.mainloop()

                    else:
                        self.user = None
                        self.konto = None
                        return self.mainloop()

                else:
                    return

    def yes_or_no_question(self, text: Optional[str] = "J / N: ") -> bool:
        """ Ask the user a simple Yes or No question """
        while True:
            choice = input(text)

            try:
                return self.yes_no_answer_choices[choice]

            except KeyError:
                print(Fore.LIGHTRED_EX + f"Ungültige Auswahl '{choice}'.")
                print(Fore.LIGHTRED_EX + "Bitte erneut eingeben.")
                continue

    def pick_action(self,
                    actions: List[Tuple[str, Callable]]
                    ) -> Callable[[], Optional[Any]]:
        print(Fore.LIGHTGREEN_EX +
            "Bitte wählen sie eine Aktion aus dem unteren Menü aus, "
            "um fortzufahren.\n"
        )

        while True:
            for index, (text, _) in enumerate(actions):
                print(Fore.LIGHTGREEN_EX + f"{index + 1}. {text}")

            try:
                selected_action = int(input())

                if selected_action <= 0:
                    raise ValueError

                action = actions[selected_action - 1][-1]

            except ValueError:
                print(Fore.LIGHTRED_EX +
                    "Die Eingabe muss eine positive, "
                    "ganze Zahl aus dem oben angezeigten Menü sein.\n"
                )
                print(Fore.LIGHTRED_EX + "Bitte erneut eingeben!")
                continue

            except IndexError:
                print(Fore.LIGHTRED_EX + "Keine gültige Aktion ausgewählt.")
                print(Fore.LIGHTRED_EX + "Bitte erneut eingeben!")
                continue

            else:
                return action

    def user_actions(self) -> None:
        actions = [
            ("Login", self.user_login),
            ("Neuen Nutzer erstellen", self.user_create),
            ("Bestehenden Nutzer löschen", self.user_delete)
        ]

        print(Fore.LIGHTRED_EX +"Sie sind aktuell nicht eingeloggt.\n")
        action = self.pick_action(actions)

        self.user = action()
        return

    def user_login(self) -> Kunde:
        while True:
            print(Fore.LIGHTGREEN_EX + "\n========LOGIN========")
            username = input("Username: ")
            password = getpass("Passwort: ")
            user = Kunde.objects.login_user(username, password)
            if user:
                return user

            print(Fore.LIGHTRED_EX + "Falsches Passwort oder Username.")
            print(Fore.LIGHTGREEN_EX + "Möchten sie stattdessen einen neuen Account erstellen?")

            if self.yes_or_no_question():
                return self.user_create()

            else:
                continue

    def user_delete(self) -> None:
        user = self.user_login()
        self.do_delete_user(user)

        print(Fore.LIGHTGREEN_EX + "Löschen erfolgreich.\n")

        return None

    def user_create(self) -> Kunde:
        kundendaten= {}  # noqa dict literal

        while True:
            if not kundendaten:
                kundendaten["name"] = input("Vor und Nachname: ")
                kundendaten["strasse"] = input("Straße und Hausnummer: ")
                kundendaten["stadt"] = input("Stadt: ")
                kundendaten["plz"] = input("Postleitzahl: ")

                while True:
                    print("Bitte geben sie ihr Geburtsdatum ein.")
                    print("Format: dd mm yyyy")
                    geb_date = input()

                    try:
                        d, m, y = [int(i) for i in geb_date.split()]
                        kundendaten["geb_date"] = date(
                            day=d,
                            month=m,
                            year=y
                        )
                        break

                    except ValueError:
                        print(Fore.LIGHTRED_EX + "Ungültiger Werte für Datum.")
                        print(Fore.LIGHTRED_EX + "Bitte erneut eingeben.")
                        continue

            kundendaten["username"] = input("Username: ")
            kundendaten["password"] = Kunde.objects.hash_password(
                getpass("Passwort: ")
            )

            try:
                kunde = Kunde(**kundendaten)
                kunde.objects.save()
                return kunde

            except ObjectAlreadyExists:
                print(Fore.LIGHTRED_EX + "\nEin Nutzer mit dem gewählten Nutzername existiert bereits.\n")
                print("Wenn sie den Nutzernamen anpassen wollen, wählen sie jetzt 'J'.")
                print("Andernfalls können sie sich anmelden, wählen sie dafür 'N'.")

                if self.yes_or_no_question(text=""):
                    continue

                else:
                    return self.user_login()

            except AssertionError as exc:
                try:
                    message = exc.args[0]

                except AttributeError or IndexError:
                    message = Fore.LIGHTRED_EX + "Einer der eingegebenen Werte ist ungültig."

                print(message)
                print(Fore.LIGHTRED_EX + "Bitte geben sie ihre Daten erneut ein.\n")
                kundendaten = {}

    def konto_selection_actions(self):
        actions = [
            ("Bestehendes Konto auswählen", self.konto_select),
            ("Neues Konto eröffnen", self.konto_create),
            ("Bestehendes Konto löschen", self.konto_delete)
        ]

        print(Fore.LIGHTRED_EX + "Aktuell haben Sie kein Konto ausgewählt.\n")
        action = self.pick_action(actions)

        self.konto = action()
        return

    def show_konten(self, konten: List[Konto]) -> None:
        if not konten:
            print(Fore.LIGHTRED_EX + "Es sind keine Konten verfügbar.")
            return

        for i, konto in enumerate(konten):
            print(Fore.LIGHTGREEN_EX + f"\n{i + 1}. {konto.kontonummer}:")
            print(
                f"Kontostand: {self._format_balance(konto.kontostand)}\n"
            )

    def konto_delete(self) -> None:
        konten = self.user.konten

        if len(konten) == 1:
            print(Fore.LIGHTRED_EX + "Sie müssen maximal ein Konto haben.")
            print(Fore.LIGHTRED_EX +
                "Um alle ihre Konten zu löschen, loggen sie sich aus, "
                "und löschen sie ihren Kundenaccount.\n"
            )
            return None

        self.show_konten(konten)
        konto = self.choose_bank_account(konten)
        self.do_delete_bank_account(konto)

        return None

    def konto_create(self) -> None:
        konto = Konto(
            besitzer=self.user.pk
        )
        konto.objects.save()

        print(Fore.LIGHTGREEN_EX +
            "Neues Konto wurde erstellt, "
            f"ihre Kontonummer ist: '{konto.kontonummer}'."
        )

        return None

    def konto_select(self) -> Konto:
        konten = self.user.konten

        self.show_konten(konten)
        konto = self.choose_bank_account(konten)

        return konto

    def choose_bank_account(self, konten: List[Konto]) -> Optional[Konto]:
        if not konten:
            return None

        # Now let the user choose their account,
        # either by account-id or the numeric index of the listing

        while True:
            selection = input(
                "Bitte wählen sie ein Konto aus der Liste: "
            )

            try:
                # Check if the user provided a numeric index
                selection = int(selection)

                if selection <= 0:
                    raise IndexError

                return konten[selection - 1]

            except ValueError:
                # the user provided an account-id
                for konto in konten:
                    if getattr(konto, "kontonummer") == selection:
                        return konto

                continue

            except IndexError:
                # An integer was provided but it didnt fit an index
                # in the users bank account list
                print(Fore.LIGHTRED_EX + f"Kein verfügbares Konto an der Stelle {selection}.")
                continue

    def perform_actions(self):
        # Select action
        action = self.select_action()

        action()

        if action.__name__ != "_show_balance":
            self._show_balance()

    def select_action(self) -> Callable[[], None]:
        actions = [
            ("Einzahlung\n", self._do_deposit),
            ("Auszahlung\n", self._do_withdraw),
            ("Überweisung tätigen\n", self._do_transfer),
            ("Kontostand anzeigen", self._show_balance)
        ]

        return self.pick_action(actions)

    def _do_deposit(self) -> None:
        while True:
            print(Fore.LIGHTGREEN_EX + "Wie viel möchten Sie einzahlen?")

            try:
                einzahlung = input()
                einzahlung = self._format_deposit(einzahlung)
                break

            except ValueError as exc:
                print(exc.args[0])
                print(Fore.LIGHTRED_EX + "Bitte geben sie einen gültigen Wert ein.")
                continue

        self.do_deposit(einzahlung)  # noqa ref before assignment

    def _do_withdraw(self) -> None:
        while True:
            print(Fore.LIGHTGREEN_EX + "Wie viel möchten Sie abheben?")

            try:
                auszahlung = input()
                auszahlung = self._format_deposit(auszahlung)

                if auszahlung > self.konto.kontostand:
                    print(Fore.LIGHTRED_EX +
                        "Sie können nicht mehr als den verfügbaren Saldo von "
                        f"{self.show_balance(self.konto)} "
                        "abheben."
                    )
                    continue

                break

            except ValueError as exc:
                print(exc.args[0])
                print(Fore.LIGHTRED_EX + "Bitte geben Sie einen gültigen Wert ein.")
                continue

        self.do_withdraw(auszahlung)  # noqa ref before assignment

    def _do_transfer(self) -> None:
        print(Fore.LIGHTGREEN_EX +
            "Sie können entweder auf eines ihrer eigenen Konten,\n"
            "oder auf das Konto einer anderen Person Geld überweisen.\n"
        )
        print(Fore.LIGHTBLUE_EX + "Eigenen Konten, welche als Ziel gelten können:")
        self.show_konten([
            k for k in self.user.konten if not k.kontonummer == self.konto.kontonummer
        ])

        while True:
            print(Fore.LIGHTGREEN_EX + "Bitte wählen sie ein Konto zu dem die Geld überweisen wollen.\n")
            kontonummer = input("Kontonummer: ")

            if kontonummer == self.konto.kontonummer:
                print(Fore.LIGHTRED_EX + "Sie können keine Überweisung auf das aktuell gewählte Konto machen.")
                print(Fore.LIGHTRED_EX + "Bitte erneut eingeben!")
                continue

            try:
                konto = Konto.objects.get(kontonummer)

            except ObjectNotFound:
                print(Fore.LIGHTRED_EX + "Kein Konto mit der angegebenen Kontonummer gefunden\n")
                print(Fore.LIGHTGREEN_EX + "Möchten sie den Prozess abbrechen oder ein anderes Konto wählen?")

                if self.yes_or_no_question(text="Abbrechen (J) / Weitermachen (N): "):
                    return

                else:
                    continue

            else:
                break

        print(Fore.LIGHTGREEN_EX +
            f"Überweisung von '{self.konto.kontonummer}' -> '{konto.kontonummer}'\n"  # noqa
        )
        print(Fore.LIGHTGREEN_EX + "Welche Summe wollen sie überweisen?")

        while True:
            try:
                summe = input()
                summe = self._format_deposit(summe)

                if summe > self.konto.kontostand:
                    print(Fore.LIGHTRED_EX +
                        "Sie können nicht mehr als den verfügbaren Saldo von "
                        f"{self.show_balance(self.konto)} "
                        "abheben."
                    )
                    continue

                break

            except ValueError as exc:
                print(exc.args[0])
                print(Fore.LIGHTRED_EX + "Bitte geben sie einen gültigen Wert ein.")
                continue

        self.do_transfer(summe, konto, self.konto)

    def _show_balance(self) -> None:
        print(Fore.LIGHTGREEN_EX + "Der aktuelle Kontostand beträgt:")
        print(self.show_balance())
