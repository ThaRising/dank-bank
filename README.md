# Dank Bank Inc.

Your trusted choice for all
banking and monetary transfer
business.

### Requirements

Python v3.8+

## Installation
Fetch master branch from github. 
> git clone https://github.com/ThaRising/dank-bank

Install packages:
>pip install -r requirements.txt

Or with Poetry:
>poetry install

## Features

#### Multiple Data Storage Types

Currently supported formats for
data storage:
- JSON
- SQL (Any RDBMS supported by SQLAlchemy)

Support for:
- Full CRUD in both Formats
- Simple Filtering
- Unique Keys / Primary Keys + Uniqueness Checks
- Persisting Schemas (JSON and SQL)

#### Simple Syntax

Example - Retrieve all Customers:
````python
Storage("sql")
Storage().db.create()

kunden = Kunde.objects.all()
print(kunden)

Storage().db.destroy()
````

#### Limitations

Not supported (or only indirectly):
- Direct relationship traversal
- Defaults declared in SQLA Column types
- Filtering Parameters e.g. name__in,
all filtering is exact

## Usage - Examples

Create SQL Database:
````python
from src.storage import Storage

# Initialize Storage
Storage("sql")
Storage().db.create()

# Do Stuff

# Clear Database
Storage().db.destroy()
````

Create JSON Database:
````python
from src.storage import Storage

Storage("json")
Storage().db.create()

# Do Stuff

Storage().db.destroy()
````

Create a Customer:
````python
from src.storage import Storage, models
import datetime

Storage("sql")
Storage().db.create()

kunde = models.Kunde(
    name="Ben Koch",
    username="ben.koch",
    password="security420",
    plz="16386",
    stadt="Berlin",
    strasse="fgr rgtert ergert ergtert",
    geb_date=datetime.date(2000, 1, 1)
)
kunde.objects.save()
````

Retrieve a customer by their username:
````python
from src.storage import Storage, models

Storage()

kunde_koch = models.Kunde.objects.read(
    username="ben.koch"
)
# Returns a list of length 1 containing the user
````
