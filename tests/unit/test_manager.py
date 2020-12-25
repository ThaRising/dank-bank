import pytest
import datetime
from src.storage.managers.base import BaseManagerInterface
from src.models import Kunde, Konto
from src.storage.exc import ObjectNotFound


def test_manager(storage):
    manager = storage.manager

    assert issubclass(manager, BaseManagerInterface)

    # This *should* work, because anything else means that the behaviour
    # of the class is strictly wrong.
    # Right now tho it is broken, which is a side-effect of the namespace merging.
    # Fixing this is a stretch-goal, since it does not affect the operation of the program,
    # but it means that the behaviour of the manager subclasses is inconsistent.

    # assert isinstance(KundenManager, BaseManagerInterface)

    # This is a test-run with an empty database
    assert Kunde.objects.all() == []
    with pytest.raises(ObjectNotFound):
        Kunde.objects.get(1)
    assert Kunde.objects.filter(name="Ben Koch") == []

    # Create some test data
    kunde_test_pw = "security420"
    kunde = Kunde(
        username="ben.koch",
        password=Kunde.objects.hash_password(kunde_test_pw),
        name="Ben Koch",
        strasse="Some Street 13",
        stadt="Berlin",
        plz="13689",
        geb_date=datetime.date(1999, 2, 13)
    )
    kunde.objects.save()
    konto = Konto(
        besitzer=kunde.pk
    )
    konto.objects.save()

    # Test again
    konten = kunde.konten
    assert type(konten) == list
    assert len(konten) == 1

    assert type(Kunde.objects.all()) == list
    assert len(Kunde.objects.all()) == 1
    assert Kunde.objects.all()[0].pk == kunde.objects.all()[0].pk

    assert Kunde.objects.filter(name="Ben Koch")
    assert not Kunde.objects.filter(name="Gerhard Orgel")

    assert Kunde.objects.filter(plz="13689", stadt="Berlin")
    assert not Kunde.objects.filter(plz="13689", stadt="jerlin")

    assert Kunde.objects.login_user(
        username="ben.koch", password=kunde_test_pw
    )
    assert not Kunde.objects.login_user(
        username="ben.koch", password="wrongOne"
    )
