from abc import ABC, abstractmethod
from typing import ClassVar, Optional

from src.storage import Storage
from src import models


class UI(ABC):
    storage_types: ClassVar[dict] = {
        "sql": lambda: Storage("sql"),
        "json": lambda: Storage("json")
    }

    storage: Storage
    user: Optional[models.Kunde]
    konto: Optional[models.Konto]

    def __init__(self, storage: Optional[Storage] = None) -> None:
        self.user = None
        self.konto = None

    @classmethod
    def _format_balance(cls, amount: int) -> str:
        balance = f"{amount!s:0>4}"
        return f"{balance[:-2]}.{balance[-2:]}€"

    @classmethod
    def _format_deposit(cls, amount: str) -> int:
        """
        Properly format user input of float-format strings to integers
        like the system needs them.
        """
        if amount.startswith("-"):
            raise ValueError("Values can not be negative.")

        separators = (".", ",")

        separators_present = [(s in amount) for s in separators]

        if all(separators_present):
            raise ValueError(
                "Amount can only contain one type of separator."
            )

        elif any(separators_present):
            for e in (".", ","):
                if e in amount:
                    num, dec = amount.split(e)

                    if len(dec) > 2:
                        raise ValueError(
                            "Cannot have more than 2 decimal places."
                        )

                    amount = int(f"{num}{dec:0<2}")
                    break

        else:
            amount = int(amount)
            amount *= 100

        return amount

    @abstractmethod
    def mainloop(self):
        pass

    def do_deposit(self,
                   sum_to_deposit: int,
                   konto: Optional[models.Konto] = None
                   ) -> None:
        konto = konto or self.konto
        konto.kontostand += sum_to_deposit
        konto.objects.save()

    def do_withdraw(self,
                    sum_to_withdraw: int,
                    konto: Optional[models.Konto] = None
                    ) -> None:
        konto = konto or self.konto
        konto.kontostand -= sum_to_withdraw
        konto.objects.save()

    def do_transfer(self,
                    sum_to_transfer: int,
                    to_konto: models.Konto,
                    from_konto: Optional[models.Konto] = None
                    ) -> None:
        from_konto = from_konto or self.konto
        self.do_withdraw(sum_to_transfer, from_konto)
        self.do_deposit(sum_to_transfer, to_konto)

    def show_balance(self, konto: Optional[models.Konto] = None):
        konto = konto or self.konto
        return self._format_balance(konto.kontostand)
