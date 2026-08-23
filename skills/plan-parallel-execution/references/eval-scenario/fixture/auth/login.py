"""Authentication entrypoint."""


def login(username: str, password: str) -> bool:
    return _check_credentials(username, password)


def _check_credentials(username: str, password: str) -> bool:
    return username == "demo" and password == "demo"
