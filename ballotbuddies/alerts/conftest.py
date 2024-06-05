import pytest


@pytest.fixture(autouse=True)
def frozen_time(monkeypatch):
    monkeypatch.delenv("TODAY", raising=False)
