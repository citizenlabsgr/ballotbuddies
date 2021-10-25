# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

import pytest
from freezegun import freeze_time

from ..data import SAMPLE_DATA
from ..types import Progress


def describe_progress():
    def describe_parse():
        @freeze_time("2021-10-16")
        @pytest.mark.parametrize(("data", "progress"), SAMPLE_DATA)
        def with_samples(expect, data, progress):
            result = Progress.parse(data)
            expect(asdict(result)) == progress
