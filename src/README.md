# Developer Documentation

This is a complete documentation
of the UI and Storage components
of this project.

Utilities used by both systems,
are located at [**src.utils**](utils).

[UI Docs](#UI)  
[Storage Documentation](#Storage)

## UI

The UI implementations
and their respective components
can be found under [**src.ui**](ui).

All UI implementations,
must be compliant with the
Abstract Baseclass: **UI**,
which can be found under
[**src.ui.base.UI**](ui/base.py).

They must also support both
a user supplied storage class,
and prompting the user
to select a storage type if
no default storage was supplied.

Lastly, all custom UI's, must
also automatically create the
database, like so:  
``storage.db.create()``

A minimal example of a custom
UI implementation, would look
something like this:  

````python
from src.ui import UI
from typing import Optional
from src.storage import Storage


class MyCustomUI(UI):
    def __init__(self, storage: Optional[Storage] = None) -> None:
        super().__init__(storage)
        
        if not storage:
            storage = input("Select a storage")
            
            self.storage = self.storage_types[storage]
            
        else:
            self.storage = storage
        
        self.storage.db.create()

    def mainloop(self):
        while True:
            print("Keep running!")
````

## Storage

The storage backend can be
found at [**src.storage**](storage).

All existing models are located
under [**src.models**](models).  
New ones can be added here as well.

### Using the Manager API

**Calling the Manager:**  
``Model.objects``

Example:  
``Kunde.objects.all()``

*.save()*  
Save the current object to the database.  
Can also be used to update the content of
the database with this object.  

Raises src.storage.exc.ObjectAlreadyExists
if the object does not pass UNIQUE checks.

**DEPRECATED as of 26.12.2020**  
*.update()*  
Save the state of the object in the database.
Returns the updated instance.  
This API is deprecated and will no longer work!

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

### Examples

Create SQL Database:
````python
from src.storage import Storage

# Initialize Storage
storage = Storage("sql")
storage.db.create()

# Do Stuff

# Clear Database
storage.db.destroy()
````

Create JSON Database:
````python
from src.storage import Storage

storage = Storage("json")
storage.db.create()

# Do Stuff

storage.db.destroy()
````

Create a Customer:

````python
from src.storage import Storage
from src.models import Kunde, Konto
import datetime

# Initialize the storage as seen above

kunde = Kunde(
    name="Ben Koch",
    username="ben.koch",
    password=Kunde.objects.hash_password("security420"),
    plz="16386",
    stadt="Berlin",
    strasse="fgr rgtert ergert ergtert",
    geb_date=datetime.date(2000, 1, 1)
)
kunde.objects.save()
````

Retrieve a customer by their username:
````python
kunde_koch = Kunde.objects.filter(
    username="ben.koch"
)
# Returns a list of length 1 containing the user
````

Retrieve a bank-account by its ID:
````python
kontonummer = "123abchiuiui"
my_id = Konto.objects.get(kontonummer)
````

Get all customers:
````python
kunden = Kunde.objects.all()
````
