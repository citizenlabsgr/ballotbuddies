# pylint: disable=access-member-before-definition,attribute-defined-outside-init

from time import time

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User


def normalize(name: str) -> str:
    return name.lower().translate({ord(c): None for c in "-_ "})


class CustomUser:
    @property
    def full_name(self: User) -> str:
        return self.get_full_name()

    @property
    def display_name(self: User) -> str:
        return self.get_full_name() or self.email

    @property
    def is_trackable(self: User) -> bool:
        return (
            self.is_authenticated
            and "@example.com" not in self.email
            and "admin" not in self.username
        )

    def update_name(self: User, request, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name
        if self.username != "admin":  # preserve default localhost user
            self.username = f"{self.get_full_name()} ({self.email})"
        self.set_password(str(int(time())))
        update_session_auth_hash(request, self)
        self.save()


for _name in dir(CustomUser):
    if not _name.startswith("_"):
        method = getattr(CustomUser, _name)
        User.add_to_class(_name, method)
