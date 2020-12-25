# Dank Bank Inc.

The "Dank Bank Inc." is an
imaginary bank, created as part
of a school project.

This repository contains
the "Frontend" and "Backend"
for this bank, which includes
tools such as:
- Tkinter based GUI
- Console based TUI
- Storage Backend with support 
  for JSON and SQL

### Requirements

To run this project, you need:  
Python v3.8.x

This project has been verified
working on **Debian 10**,
**WSL** running **Debian 9**
and **Windows 10 1909**.

### Optional Dependencies

To fully interact with the
dependencies and the
Virtual Environment, the
following is additionally required:
- Python Poetry
- make
- gcc

## Installation

Download this repository from GitHub:  
``git clone https://github.com/ThaRising/dank-bank``

Install dependencies using pip:  
``python -m pip install -r requirements.txt``

Or using Poetry (preferred):  
``poetry install``

## Running the Project

The entrypoint for this project
is the *main.py* file.

You should adjust the content
of the *main.py* file, depending
on which type of UI you want to use.

If you want to use the GUI:  
````python
# main.py

from src.ui import GUI


if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
````

Or, if you want to use the
TUI instead:  
````python
# main.py

from src.ui import TUI


if __name__ == '__main__':
    tui = TUI()
    tui.mainloop()
````

Both of the UI variations,
will prompt the user to select
their Storage-type of choice on
start-up.

If you want to use a specific
Storage for the UI, you can
pass it as a parameter like so:  
````python
# main.py

from src.ui import TUI
from src.storage import Storage


if __name__ == '__main__':
    storage = Storage("sql")
    tui = TUI(storage)
    tui.mainloop()
````

Once the main.py has been adjusted,
you can run it using pip via:  
``python main.py``  


Or using Poetry:  
``poetry run python main.py``

## Features

### Fully featured UI

This project comes with a
complete GUI and TUI,
each of which allow full
interaction with the
imaginary bank.

The following is supported:
- Creating Users
- Creating Bank accounts for users
- Multiple Actions for Bank accounts:
  - Deposit Money
  - Withdraw Money
  - Transfer Money to other accounts
  - Viewing account balance

### Complete Storage Backend

A full storage backend comes
included with this repository.

It features an easy-to-use
Active Record like syntax and
supports intuitive querying for objects.

It also has support for all major RDBMS
and even local JSON data storage
and comes with a unified API for all
supported data storage options.

#### Multiple Data Storage Types

Supported formats for data storage:
- JSON
- SQL (Any RDBMS supported by SQLAlchemy)

Support for:
- Full CRUD in both Formats
- Simple Filtering
- Unique Keys / Primary Keys + Uniqueness Checks
- Persisting Data (JSON and SQL)

#### Simple Querying of objects

````python
from src.models import Kunde

# Retrieve all customers named 'Ben Koch'
customers = Kunde.objects.filter(name="Ben Koch")

# Retrieve all customers in the database
customers = Kunde.objects.all()

# Get a customer by their user-id
customer = Kunde.objects.get("1692523d91ec4e8d9f0791f3a0718dcc")
````

#### Simple declaration of new Models

````python
# src/models/item.py

from drizm_commons.sqla import Base

from src.storage.managers import BaseManager, ManagerMixin
import sqlalchemy as sqla
import uuid


class Item(ManagerMixin, Base):
    manager = BaseManager

    pk = sqla.Column(sqla.String, primary_key=True)
    color = sqla.Column(sqla.String)
    item_name = sqla.Column(sqla.String)

    def __init__(self, **kwargs) -> None:
        # generate a default primary key
        if not kwargs.get("pk"):
          kwargs["pk"] = uuid.uuid4()

        super().__init__(**kwargs)
````

## Storage Limitations

Not supported (or only indirectly):
- Direct relationship traversal
- Defaults declared in SQLA Column types
- Filtering Parameters e.g. a Django-Style
"name__in", all filtering is exact and
case-sensitive
- Numeric Auto-Incrementing PrimaryKeys

## API Documentation

[Jump to the Technical Docs!](src/README.md)

You can find the API docs
(or technical documentation so to speak)
in the *src* folder.

There you will find the information
you need to use the Storage backend,
as well as a full documentation of
the API for both the UI and the Storage.
