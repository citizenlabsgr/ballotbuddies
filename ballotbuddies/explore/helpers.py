from time import time

from django.core.cache import cache

import httpx
import log

API = "https://michiganelections.io/api"


async def get_election(election_id: int) -> dict:
    url = f"{API}/elections/{election_id}/"
    async with httpx.AsyncClient() as client:
        data = await _call(client, url, cache_result=True)
        return data


async def get_district(district_id: int) -> dict:
    url = f"{API}/districts/{district_id}/"
    async with httpx.AsyncClient() as client:
        data = await _call(client, url, cache_result=True)
        return data


async def get_proposals(
    q: str, limit: int, *, election_id: int = 0, district_id: int = 0
) -> tuple[int, list]:
    total = 0
    items: list[dict] = []

    log.info(f"Getting proposals: {election_id=} {district_id=} {q=}")
    url = f"{API}/proposals/?active_election=null"
    url += "&limit=1000" if limit else "&limit=1"
    if election_id:
        url += f"&election_id={election_id}"
    if district_id:
        url += f"&district_id={district_id}"

    start = time()
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while url:
            data = await _call(client, url, cache_result=not limit)
            total = data["count"]
            url = data["next"]
            if q:
                for item in data["results"]:
                    text = item["name"].lower() + item["description"].lower()
                    if q.lower() in text:
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

    log.info(f"Getting {limit} positions: {election_id=} {district_id=} {q=}")
    url = f"{API}/positions/?active_election=null"
    url += "&limit=1000" if limit else "&limit=1"
    if election_id:
        url += f"&election_id={election_id}"
    if district_id:
        url += f"&district_id={district_id}"

    start = time()
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while url:
            data = await _call(client, url, cache_result=not limit)
            total = data["count"]
            url = data["next"]
            if q:
                for item in data["results"]:
                    text = item["name"].lower() + item["description"].lower()
                    if q.lower() in text:
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


async def _call(client, url: str, *, cache_result: bool = False) -> dict:
    if cache_result:
        data = await cache.aget(url)
        if data is None:
            log.info(f"Fetching {url}")
            response = await client.get(url)
            data = response.json()
            await cache.aset(url, data, timeout=60 * 60)
    else:
        log.info(f"Fetching {url}")
        response = await client.get(url)
        data = response.json()

    return data
