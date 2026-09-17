from dataclasses import dataclass


@dataclass
class User:
    name: str
    active: bool = True


def create_user(name: str) -> User:
    if not name.strip():
        raise ValueError("name is required")
    return User(name=name)


def deactivate_user(user: User) -> None:
    user.active = False
