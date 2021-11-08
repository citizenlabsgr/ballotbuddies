# pylint: disable=redefined-outer-name,unused-variable,expression-not-assigned

from . import user


def describe_login():
    def it_displays_site_name(expect):
        user.visit("/admin")

        expect(user.browser.title) == "Log in | Ballot Buddies Admin"
