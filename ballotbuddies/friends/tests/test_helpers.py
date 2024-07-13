# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

import pytest

from .. import helpers


@pytest.mark.django_db
def test_update_neighbors(expect):
    helpers.generate_sample_voters()
    expect(helpers.update_neighbors()) == 0


@pytest.mark.django_db
def test_update_statuses(expect):
    helpers.generate_sample_voters()
    expect(helpers.update_statuses()) == 0
