import httpx
import log

API = "https://michiganelections.io/api"


async def get_election(election_id: int) -> dict:
    url = f"{API}/elections/{election_id}/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


async def get_proposals(*, election_id: int = 0, count: int = 20) -> list:
    items: list[dict] = []

    url = f"{API}/proposals/?active_election=null"
    if election_id:
        url += f"&election_id={election_id}"

    async with httpx.AsyncClient() as client:
        while url and len(items) < count:
            log.info(f"Fetching {url}")
            response = await client.get(url)
            data = response.json()
            items.extend(data["results"])
            url = data["next"]

    return items[:count]
