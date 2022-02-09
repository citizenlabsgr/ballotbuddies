from splinter import Browser

site: str = ""
browser: Browser = None


def visit(path):
    browser.visit(site + path)


def login(email: str):
    visit("/login")
    browser.fill("email", email)
    browser.find_by_text("Log in").click()


def logout():
    visit("/logout")
