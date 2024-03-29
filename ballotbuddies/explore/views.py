from django.http import HttpRequest
from django.shortcuts import redirect, render

import log
from asgiref.sync import sync_to_async

from . import constants, helpers

async_render = sync_to_async(render)


def index(request: HttpRequest):
    if request.GET.get("referrer") and request.user.is_authenticated:
        return redirect("buddies:profile")
    return redirect("explore:proposals")


async def proposals_list(request: HttpRequest):
    return await _filter_proposals(request)


async def proposals_by_election(request: HttpRequest, election_id: int):
    return await _filter_proposals(request, election_id=election_id)


async def proposals_by_district(request: HttpRequest, district_id: int):
    return await _filter_proposals(request, district_id=district_id)


async def proposals_by_election_and_district(
    request: HttpRequest, election_id: int, district_id: int
):
    return await _filter_proposals(
        request, election_id=election_id, district_id=district_id
    )


async def _filter_proposals(
    request: HttpRequest, *, election_id: int = 0, district_id: int = 0
):
    q = request.GET.get("q", "").strip()
    limit = int(request.GET.get("limit", constants.LIMIT))
    banner = ""

    if election_id:
        election = await helpers.get_election(election_id)
        q = _normalize(q, election)
        banner = f"election_id={election_id}"
    else:
        election = None

    if district_id:
        district = await helpers.get_district(district_id)
        q = _normalize(q, district)
        banner = f"district_id={district_id}"
    else:
        district = None

    total, proposals = await helpers.get_proposals(
        q, limit, election_id=election_id, district_id=district_id
    )
    if proposals and not banner:
        banner = f"election_id={proposals[0]['election']['id']}"

    context = {
        "q": q,
        "election": election,
        "district": district,
        "proposals": proposals[:limit],
        "total": total,
        "count": len(proposals),
        "limit": limit,
        "banner": banner,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def positions_list(request: HttpRequest):
    return await _filter_positions(request)


async def positions_by_election(request: HttpRequest, election_id: int):
    return await _filter_positions(request, election_id=election_id)


async def positions_by_district(request: HttpRequest, district_id: int):
    return await _filter_positions(request, district_id=district_id)


async def positions_by_election_and_district(
    request: HttpRequest, election_id: int, district_id: int
):
    return await _filter_positions(
        request, election_id=election_id, district_id=district_id
    )


async def _filter_positions(
    request: HttpRequest, *, election_id: int = 0, district_id: int = 0
):
    q = request.GET.get("q", "").strip()
    limit = int(request.GET.get("limit", constants.LIMIT))
    banner = ""

    if election_id:
        election = await helpers.get_election(election_id)
        q = _normalize(q, election)
        banner = f"election_id={election_id}"
    else:
        election = None

    if district_id:
        district = await helpers.get_district(district_id)
        q = _normalize(q, district)
        banner = f"district_id={district_id}"
    else:
        district = None

    total, positions = await helpers.get_positions(
        q, limit, election_id=election_id, district_id=district_id
    )
    if positions and not banner:
        banner = f"election_id={positions[0]['election']['id']}"

    context = {
        "q": q,
        "election": election,
        "district": district,
        "positions": positions[:limit],
        "total": total,
        "count": len(positions),
        "limit": limit,
        "banner": banner,
    }

    if "limit" in request.GET:
        template_name = "explore/_positions.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def elections_list(request: HttpRequest):
    total, elections = await helpers.get_elections()

    context = {
        "elections": elections,
        "total": total,
        "banner": f"election_id={elections[0]['id']}",
    }

    return await async_render(request, "explore/index.html", context)


def _normalize(q: str, item: dict) -> str:
    label = item["name"]
    if category := item.get("category"):
        label += " " + category
    if len(q) > 3 and q.lower() in label.lower():
        log.info(f"Matched {q=} to {item}")
        return ""
    return q
