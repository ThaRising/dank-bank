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
- Numeric Auto-Incrementing PrimaryKeys

## Usage - Manager API

**Calling the Manager:**  
``Model.objects``

Example:  
``Kunde.objects.all()``

*.save()*  
Save the current object in the database.  
Raises src.storage.exc.ObjectAlreadyExists
if the object does not pass UNIQUE checks.

*.update()*  
Save the state of the object in the database.
Returns the updated instance.

*.delete()*  
Delete the current object from the database.

*.get()*  
Get an instance by its primary key.
Raises src.storage.exc.ObjectNotFound
if no object was found for the given identifier.

*.filter()*  
Get all objects from the database that match
the specified set of filter params.

*.all()*  
Get all objects of this Model from the database.

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

kunde_koch = models.Kunde.objects.filter(
    username="ben.koch"
)
# Returns a list of length 1 containing the user
````
