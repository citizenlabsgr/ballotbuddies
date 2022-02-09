# pylint: disable=redefined-outer-name,unused-variable,expression-not-assigned

from . import user


def describe_login():
    def it_prompts_to_check_email(expect):
        user.visit("/login")

        user.browser.fill("email", "test@example.com")
        user.browser.find_by_text("Log in").click()

        expect(user.browser.html).contains("Open example.com")
