# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

import pytest

from ..constants import SAMPLE_DATA
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
        @pytest.mark.parametrize("sample", SAMPLE_DATA)
        def with_samples(expect, sample):
            result = Progress.parse(sample.status)
            expect(asdict(result)) == sample.progress

    def test_sort(expect):
        items = [Progress.parse(voter.progress) for voter in SAMPLE_DATA]
        expect(sorted(items)) == items  # type: ignore
