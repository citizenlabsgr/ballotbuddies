# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

import pytest

from ..data import SAMPLE_STATUS
from ..types import Progress


def describe_progress():
    def describe_parse():
        @pytest.mark.parametrize(("status", "progress"), SAMPLE_STATUS)
        def with_samples(expect, status, progress):
            result = Progress.parse(status)
            expect(asdict(result)) == progress
