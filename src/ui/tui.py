from typing import Optional
import sys


class TUI:
    def __init__(self):
        while not (file_type := self.print_intro()):
            pass
        self.file_type = file_type

        while True:
            self.user = self.login_prompt()

            x = True    #check Variable
            while x:

                while not (option := self.choose_option()):
                    pass
                self.option = option

                self.pass_option(option)

                if not self.keep_running():
                    sys.exit(0)
                if self.change_user_or_stay_logged_in():
                    x = False


    def print_intro(self) -> Optional[int]:
        print('Wähle aus:')
        print('1 = SQL | 2 = JSON')
        try:
            file_type = int(input())
        except ValueError:
            print("Bitte geben sie einen gültigen Integer ein!\n")
            return False
        if file_type == 1:
            print('SQL wurde gewählt')
            return file_type
        elif file_type == 2:
            print('JSON wurde gewählt')
            return file_type
        else:
            print('Bitte geben sie eine gültigen Wert ein!\n')

    def login_prompt(self) -> Optional[int]:
        # idgaf about this method, get rekt
        username = str(input('Username: '))
        account_id = self.login_account_id_check()
        password = str(input('Passwort: '))
        print(username, account_id, password, '\n')
        conUser = True
        return conUser

    def login_account_id_check(self):
        while True:
            try:
                account_id = int(input('Account ID: '))
            except ValueError:
                print('Ungültige Eingabe! Bitte Integer Wert eingeben.\n')
            else:
                break
        return account_id

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
            return

    def pass_option(self, option):
        if option == "Einzahlung":
            self.option_deposit()
        elif option == "Auszahlung":
            self.option_withdraw()
        elif option == "Überweisung":
            self.option_transfer()
        elif option == "Kontostand":
            self.option_balance()
        else:
            print("öhhm etwas ist schief gelaufen")
            sys.exit(69)

    def option_deposit(self):
        print('Einzahlung wurde gewählt\n')
        #TODO Einzahlung

    def option_withdraw(self):
        print('Auszahlung wurde gewählt\n')
        #TODO Auszahlung

    def option_transfer(self):
        print('Überweisung wurde gewählt\n')
        #TODO Überweisung

    def option_balance(self):
        print('Kontostand wurde gewählt\n')
        #TODO Kontostand

    def change_user_or_stay_logged_in(self) -> Optional[int]:
        try:
            option = int(
                input('Weiter Aktionen mit diesen Account tätigen?\n1 = Ja | 2 = Nein\n')
            )
            return option - 1
        except ValueError:
            print("Ungültiger Input! Sie werden nun zurück zur Anmeldung gebracht")
            return 1

    def keep_running(self) -> Optional[int]:
        try:
            option = int(
                input('Programm beenden?\n1 = Ja | 2 = Nein\n')
            )
            return option - 1
        except ValueError:
            print("Ungültiger Input! Programm wird fortgefahren")
            return 1


if __name__ == '__main__':
    TUI()
