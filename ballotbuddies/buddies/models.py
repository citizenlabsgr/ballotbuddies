from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import log
import requests


class Voter(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    birth_date = models.DateField(null=True)
    zip_code = models.CharField(null=True, max_length=5)
    status = models.JSONField(null=True, blank=True)
    updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    @property
    def first_name(self) -> str:
        return self.user.first_name

    @property
    def last_name(self) -> str:
        return self.user.last_name

    @property
    def status_id(self) -> str:
        return (self.status or {}).get("id", "")

    def update(self) -> bool:
        previous_status_id = self.status_id

        url = f"https://michiganelections.io/api/status/?first_name={self.first_name}&last_name={self.last_name}&zip_code={self.zip_code}&birth_date={self.birth_date}"
        log.info(f"GET {url}")
        response = requests.get(url)
        if response.status_code != 200:
            log.error(f"{response.status_code} response")
            return False

        data = response.json()
        log.info(f"{response.status_code} response: {data}")
        self.status = data

        return self.status_id != previous_status_id

    def save(self, **kwargs):
        self.updated = timezone.now()
        super().save(**kwargs)
