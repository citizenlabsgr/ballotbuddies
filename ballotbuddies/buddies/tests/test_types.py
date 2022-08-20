# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

import pytest

from ..constants import SAMPLE_DATA
from ..types import Progress, to_ordinal

from django.conf import settings


@pytest.mark.parametrize(
    ("days", "ordinal"),
    [
        (1, "st"),
        (2, "nd"),
        (3, "rd"),
        (4, "th"),
    ],
)
def test_to_ordinal(expect, days, ordinal):
    expect(to_ordinal(days)) == ordinal


def describe_progress():
    def describe_sort():
        def is_based_on_values(expect):
            items = [Progress.parse(voter.progress) for voter in SAMPLE_DATA]
            expect(sorted(items)) == items  # type: ignore

    def describe_percent():
        @pytest.mark.parametrize(
            ("status", "percent"),
            [
                (SAMPLE_DATA[0].status, 0),
                (SAMPLE_DATA[1].status, 57),
                (SAMPLE_DATA[2].status, 100),
            ],
        )
        def is_based_on_progress(expect, status, percent):
            progress = Progress.parse(status)
            expect(progress.percent) == percent

    def describe_actions():
        def is_zero_for_past_elections(expect, monkeypatch):
            monkeypatch.setattr(settings, "TODAY", None)
            progress = Progress.parse(SAMPLE_DATA[1].status)
            expect(progress.actions) == 0

    def describe_parse():
        @pytest.mark.parametrize("sample", SAMPLE_DATA)
        def with_samples(expect, sample):
            result = Progress.parse(sample.status)
            expect(asdict(result)) == sample.progress
