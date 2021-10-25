# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

import pytest

from ..data import SAMPLE_DATA
from ..types import Progress


def describe_progress():
    def describe_parse():
        @pytest.mark.parametrize(("data", "progress"), SAMPLE_DATA)
        def with_samples(expect, data, progress):
            result = Progress.parse(data)
            expect(asdict(result)) == progress
