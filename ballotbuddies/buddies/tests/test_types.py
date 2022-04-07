# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

import pytest
from freezegun import freeze_time

from ..data import SAMPLE_DATA
from ..types import Progress, to_ordinal


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
    def describe_parse():
        @freeze_time("2021-10-16")
        @pytest.mark.parametrize(("data", "progress"), SAMPLE_DATA)
        def with_samples(expect, data, progress):
            result = Progress.parse(data)
            expect(asdict(result)) == progress

    def test_sort(expect):
        items = [Progress.parse(p[1]) for p in SAMPLE_DATA]
        expect(sorted(items)) == items  # type: ignore
