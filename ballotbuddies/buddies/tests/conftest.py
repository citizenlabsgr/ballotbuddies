import pytest

from .. import constants


@pytest.fixture(autouse=True)
def default_constants(monkeypatch):
    monkeypatch.setattr(
        constants,
        "PRECINCT_PREVIEW_URL",
        constants.PRECINCT_PREVIEW_URL.replace(
            "http://localhost:5000", "https://share.michiganelections.io"
        ),
    )
    monkeypatch.delenv("TODAY", raising=False)
