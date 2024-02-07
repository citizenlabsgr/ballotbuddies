# pylint: disable=redefined-outer-name,unused-variable,unused-argument,expression-not-assigned

import pytest


def describe_index():
    def it_redirects_to_proposals(expect, client):
        response = client.get("/explore/")
        expect(response.status_code) == 302
        expect(response.url) == "/explore/proposals/"


def describe_proposals():
    @pytest.mark.vcr
    def it_shows_proposals_loading_message(expect, client):
        response = client.get("/explore/proposals/?limit=0")
        html = response.content.decode()
        expect(html).contains("Loading 8094 proposals")

    def it_shows_proposals_by_election(expect, client):
        response = client.get("/explore/proposals/election/54/")
        html = response.content.decode()
        expect(html).contains("Presidential Primary")

    def it_shows_proposals_by_district(expect, client):
        response = client.get("/explore/proposals/district/729/")
        html = response.content.decode()
        expect(html).contains("Township of Marcellus")

    def it_shows_proposals_by_election_and_district(expect, client):
        response = client.get("/explore/proposals/election/54/district/728/")
        html = response.content.decode()
        expect(html).contains("Presidential Primary")
        expect(html).contains("Cass")

    @pytest.mark.vcr
    def it_filters_proposals_by_text(expect, client):
        response = client.get("/explore/proposals/election/54/?q=money")
        html = response.content.decode()
        expect(html.count("money")) == 11


def describe_positions():
    @pytest.mark.vcr
    def it_shows_positions_loading_message(expect, client):
        response = client.get("/explore/positions/?limit=0")
        html = response.content.decode()
        expect(html).contains("Loading 49139 positions")

    def it_shows_positions_by_election(expect, client):
        response = client.get("/explore/positions/election/54/")
        html = response.content.decode()
        expect(html).contains("Presidential Primary")

    def it_shows_positions_by_district(expect, client):
        response = client.get("/explore/positions/district/729/")
        html = response.content.decode()
        expect(html).contains("Township of Marcellus")

    def it_shows_positions_by_election_and_district(expect, client):
        response = client.get("/explore/positions/election/54/district/728/")
        html = response.content.decode()
        expect(html).contains("Presidential Primary")
        expect(html).contains("Cass")

    @pytest.mark.vcr
    def it_filters_positions_by_text(expect, client):
        response = client.get("/explore/positions/election/54/?q=taxes")
        html = response.content.decode()
        expect(html.count("taxes")) == 7


@pytest.mark.vcr
def describe_elections():
    def it_shows_all_elections(expect, client):
        response = client.get("/explore/elections/")
        html = response.content.decode()
        expect(html.count("<li>")) == 22
