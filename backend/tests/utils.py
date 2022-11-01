import json


def get_fixture(path: str) -> dict:
    with open(f"fixtures/api/{path}") as file:
        return json.load(file)
