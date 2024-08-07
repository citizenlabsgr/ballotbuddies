# pylint: disable=unused-variable,expression-not-assigned


def describe_index():
    def it_redirects_to_proposals(expect, client):
        response = client.get("/explore/")
        expect(response.status_code) == 302
        expect(response.url).contains("proposals")


def describe_proposals():
    def it_shows_proposals_loading_message(expect, client):
        response = client.get("/explore/proposals/?limit=0")
        html = response.content.decode()
        expect(html).contains("Loading")

    def it_shows_proposals_by_election(expect, client):
        response = client.get("/explore/proposals/election/54/")
        html = response.content.decode()
        expect(html).contains("Presidential Primary")
        expect(html).contains("banner.jpg?election_id=54")

    def it_shows_proposals_by_district(expect, client):
        response = client.get("/explore/proposals/district/729/")
        html = response.content.decode()
        expect(html).contains("Township of Marcellus")
        expect(html).contains("banner.jpg?district_id=729")

    def it_shows_proposals_by_election_and_district(expect, client):
        response = client.get("/explore/proposals/election/54/district/728/")
        html = response.content.decode()
        expect(html).contains("1 Item")
        expect(html).contains("Presidential Primary")
        expect(html).contains("Cass")
        expect(html).contains("banner.jpg?district_id=728")

    def it_filters_proposals_by_text(expect, client):
        response = client.get("/explore/proposals/election/54/?q=money")
        html = response.content.decode()
        expect(html.count("money")) == 12


def describe_positions():
    def it_shows_positions_loading_message(expect, client):
        response = client.get("/explore/positions/?limit=0")
        html = response.content.decode()
        expect(html).contains("Loading")

    def it_shows_positions_by_election(expect, client):
        response = client.get("/explore/positions/election/54/")
        html = response.content.decode()
        expect(html).contains("4 Items")
        expect(html).contains("Presidential Primary")
        expect(html).contains("banner.jpg?election_id=54")

    def it_shows_positions_by_district(expect, client):
        response = client.get("/explore/positions/district/729/")
        html = response.content.decode()
        expect(html).contains("Township of Marcellus")
        expect(html).contains("banner.jpg?district_id=729")

    def it_shows_positions_by_election_and_district(expect, client):
        response = client.get("/explore/positions/election/54/district/728/")
        html = response.content.decode()
        expect(html).contains("0 Items")
        expect(html).contains("Presidential Primary")
        expect(html).contains("Cass")
        expect(html).contains("banner.jpg?district_id=728")

    def it_filters_positions_by_text(expect, client):
        response = client.get("/explore/positions/election/54/?q=taxes")
        html = response.content.decode()
        expect(html.count("taxes")) == 8


def describe_elections():
    def it_shows_all_elections(expect, client):
        response = client.get("/explore/elections/")
        html = response.content.decode()
        expect(html.count("<li>")) >= 24
