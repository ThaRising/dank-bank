from tkinter import Entry
from datetime import date


class DateEntry(Entry):
    def get(self):
        val = super(DateEntry, self).get()

        try:
            d, m, y = [int(i) for i in val.strip().split()]
            return date(day=d, month=m, year=y)
        except ValueError:
            raise AssertionError("Ungültiges Datumsformat.")
