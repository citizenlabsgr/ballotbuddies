from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from ballotbuddies.buddies.models import Voter


class Command(BaseCommand):

    help = "Generate data for automated testing and manual review"

    def add_arguments(self, parser):
        parser.add_argument(
            "voters",
            nargs="?",
            type=lambda value: value.split("/"),
            default=[],
        )

    def handle(self, *, voters, **_options):
        self.update_site()
        self.get_or_create_superuser()
        self.get_or_create_user("newbie@example.com")
        for voter in voters:
            info = voter.split(",")
            self.get_or_create_voter(*info)

    def update_site(self):
        site = Site.objects.get(id=1)
        site.name = f"Ballot Buddies {settings.BASE_NAME}"
        site.domain = settings.BASE_DOMAIN
        site.save()
        self.stdout.write(f"Updated site: {site}")

    def get_or_create_superuser(self, username="admin", password="password"):
        try:
            user = User.objects.create_superuser(
                username=username,
                email=f"{username}@{settings.BASE_DOMAIN}",
                password=password,
            )
            self.stdout.write(f"Created superuser: {user}")
        except IntegrityError:
            user = User.objects.get(username=username)
            self.stdout.write(f"Found superuser: {user}")

        return user

    def get_or_create_user(self, base_email: str, password="password"):
        username, email_domain = base_email.split("@")

        user, created = User.objects.get_or_create(username=username)
        if email_domain == "example.com":
            user.email = base_email
        else:
            user.email = f"{username}+{settings.BASE_NAME}@{email_domain}"
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(f"Created user: {user}")
        else:
            self.stdout.write(f"Updated user: {user}")

        return user

    def get_or_create_voter(
        self,
        base_email: str,
        first_name: str,
        last_name: str,
        birth_date: str,
        zip_code: str,
    ):
        user = self.get_or_create_user(base_email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        voter, created = Voter.objects.update_or_create(
            user=user, defaults=dict(birth_date=birth_date, zip_code=zip_code)
        )

        if created:
            self.stdout.write(f"Created voter: {voter}")
        else:
            self.stdout.write(f"Updated voter: {voter}")

        return voter
