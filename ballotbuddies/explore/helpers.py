from time import time

from django.core.cache import caches

import httpx
import log

API = "https://michiganelections.io/api"

cache = caches["explore"]


async def get_election(election_id: int) -> dict:
    url = f"{API}/elections/{election_id}/"
    async with httpx.AsyncClient() as client:
        data = await _call(client, url)
        return data


async def get_district(district_id: int) -> dict:
    url = f"{API}/districts/{district_id}/"
    async with httpx.AsyncClient() as client:
        data = await _call(client, url)
        return data


async def get_proposals(
    q: str, limit: int, *, election_id: int = 0, district_id: int = 0
) -> tuple[int, list]:
    total = 0
    items: list[dict] = []

    log.info(f"Getting proposals: {election_id=} {district_id=} {q=} {limit=}")
    url = f"{API}/proposals/?active_election=null"
    url += "&limit=1000" if limit else "&limit=1"
    if election_id:
        url += f"&election_id={election_id}"
    if district_id:
        url += f"&district_id={district_id}"

    start = time()
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while url:
            data = await _call(client, url)
            total = data["count"]
            url = data["next"]
            if q:
                for item in data["results"]:
                    if _match(q, item):
                        items.append(item)
            else:
                items.extend(data["results"])

            if len(items) >= limit:
                s = "" if len(items) == 1 else "s"
                log.info(f"Stopped fetching after {len(items)} item{s}")
                break

            elapsed = round(time() - start, 1)
            if elapsed > 10:
                log.info(f"Stopped fetching after {elapsed} seconds timeout")
                break

    return total, items


async def get_positions(
    q: str, limit: int, *, election_id: int = 0, district_id: int = 0
) -> tuple[int, list]:
    total = 0
    items: list[dict] = []

    log.info(f"Getting {limit} positions: {election_id=} {district_id=} {q=} {limit=}")
    url = f"{API}/positions/?active_election=null"
    url += "&limit=1000" if limit else "&limit=1"
    if election_id:
        url += f"&election_id={election_id}"
    if district_id:
        url += f"&district_id={district_id}"

    start = time()
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while url:
            data = await _call(client, url)
            total = data["count"]
            url = data["next"]
            if q:
                for item in data["results"]:
                    if _match(q, item):
                        items.append(item)
            else:
                items.extend(data["results"])

            if len(items) >= limit:
                s = "" if len(items) == 1 else "s"
                log.info(f"Stopped fetching after {len(items)} item{s}")
                break

            elapsed = round(time() - start, 1)
            if elapsed > 10:
                log.info(f"Stopped fetching after {elapsed} seconds timeout")
                break

    return total, items


async def get_elections() -> tuple[int, list]:
    log.info("Getting elections")
    url = f"{API}/elections/"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = await _call(client, url)
        total = data["count"]
        url = data["next"]
        items = data["results"]

    return total, items


async def _call(client, url: str) -> dict:
    data = await caches["explore"].aget(url)
    if data is None:
        log.info(f"Fetching {url}")
        response = await client.get(url)
        data = response.json()
        await caches["explore"].aset(url, data)
    return data


def _match(query: str, item: dict) -> bool:
    parts = query.strip("-").split(" -", 1)
    inclusion_phrase = parts[0].strip().lower()
    exclusion_phrase = parts[1].strip().lower() if len(parts) > 1 else ""

    item_text = " ".join(
        [
            item["name"],
            item["description"],
            item["election"]["name"],
            item["district"]["name"],
        ]
    ).lower()

    if inclusion_phrase and inclusion_phrase not in item_text:
        return False

    if exclusion_phrase and exclusion_phrase in item_text:
        return False

    return True
