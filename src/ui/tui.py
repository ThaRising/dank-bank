from typing import Optional
import sys


class TUI:
    def __init__(self):
        while not (file_type := self.print_intro()):
            pass
        self.file_type = file_type

        while True:
            self.user = self.login_prompt()
            while not (option := self.choose_option()):
                pass
            if not self.keep_running():
                sys.exit(0)
            if not self.change_user_or_stay_logged_in():
                sys.exit(0)

    def print_intro(self) -> Optional[int]:
        print('Wähle aus:')
        print('1 = SQL | 2 = JSON')
        try:
            file_type = int(input())
        except TypeError:
            print("Bitte geben sie einen gültigen Integer ein, danke Ronneberg")
            return False
        if file_type == 1:
            print('SQL wurde gewählt')
            return file_type
        elif file_type == 2:
            print('JSON wurde gewählt')
            return file_type
        else:
            print('Absolut kritisch mein Freund')

    def login_prompt(self) -> Optional[int]:
        # idgaf about this method, get rekt
        str(input('Username: '))
        int(input('Account ID: '))
        str(input('Passwort: '))
        conUser = True
        return conUser

    def choose_option(self) -> Optional[int]:
        options = [
            "Einzahlung",
            "Auszahlung",
            "Überweisung",
            "Kontostand"
        ]
        print('Wähle aus:')
        [print(f"{index + 1} = {option}") for index, option in enumerate(options)]
        try:
            option = int(input())
            assert option > 0, "Gültig oder ich stech dich ab"
            chosen = options[option - 1]
            return chosen
        except TypeError:
            print("Bitte geben sie einen gültigen Integer ein, danke Ronneberg")
            return False
        except IndexError:
            print("Ist keine gültige Option")
            return False

    def change_user_or_stay_logged_in(self) -> Optional[int]:
        try:
            option = int(
                input('Weiter Aktionen mit diesen Account tätigen?\n1 = Nein | 2 = Ja\n')
            )
            return option - 1
        except TypeError:
            print("Bitte geben sie einen gültigen Integer ein, danke Ronneberg")
            return False

    def keep_running(self) -> Optional[int]:
        try:
            option = int(
                input('Programm beenden?\n1 = Nein | 2 = Ja\n')
            )
            return option - 1
        except TypeError:
            print("Programm wird fortgefahren")
            return False


if __name__ == '__main__':
    TUI()
