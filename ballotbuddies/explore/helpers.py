import httpx
import log

API = "https://michiganelections.io/api"


async def get_election(election_id: int) -> dict:
    url = f"{API}/elections/{election_id}/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


async def get_district(district_id: int) -> dict:
    url = f"{API}/districts/{district_id}/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


async def get_proposals(
    limit: int, *, election_id: int = 0, district_id: int = 0
) -> list:
    items: list[dict] = []

    url = f"{API}/proposals/?active_election=null"
    if election_id:
        url += f"&election_id={election_id}"
    if district_id:
        url += f"&district_id={district_id}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        while url and len(items) < limit:
            log.info(f"Fetching {url}")
            response = await client.get(url)
            data = response.json()
            items.extend(data["results"])
            url = data["next"]

    return items
