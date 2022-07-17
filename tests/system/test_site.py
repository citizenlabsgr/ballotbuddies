# pylint: disable=redefined-outer-name,unused-variable,expression-not-assigned

from . import user


def describe_login():
    def it_prompts_to_check_email(expect):
        user.login("test@example.com")

        expect(user.browser.html).contains("sent to your <b>example.com</b> address")
