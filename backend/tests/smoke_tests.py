import pytest


def smoke_test():
    pass


@pytest.mark.django_db(transaction=True)
def db_smoke_test():
    pass
