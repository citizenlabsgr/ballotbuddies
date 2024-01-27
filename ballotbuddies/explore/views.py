from django.http import HttpRequest
from django.shortcuts import redirect, render

from asgiref.sync import sync_to_async

from . import helpers

async_render = sync_to_async(render)


async def index(_request: HttpRequest):
    return redirect("explore:proposals")


async def proposals_by_text(request: HttpRequest):
    return await _filter_proposals(request)


async def proposals_by_election(request: HttpRequest, election_id: int):
    return await _filter_proposals(request, limit=20, election_id=election_id)


async def proposals_by_district(request: HttpRequest, district_id: int):
    return await _filter_proposals(request, limit=20, district_id=district_id)


async def proposals_by_election_and_district(
    request: HttpRequest, election_id: int, district_id: int
):
    return await _filter_proposals(
        request, limit=20, election_id=election_id, district_id=district_id
    )


async def _filter_proposals(
    request: HttpRequest, *, limit: int = 0, election_id: int = 0, district_id: int = 0
):
    q = request.GET.get("q", "").strip().lower()
    limit = int(request.GET.get("limit", limit))

    if election_id:
        election = await helpers.get_election(election_id)
    else:
        election = None

    if district_id:
        district = await helpers.get_district(district_id)
    else:
        district = None

    total, proposals = await helpers.get_proposals(
        q, limit, election_id=election_id, district_id=district_id
    )

    context = {
        "q": q,
        "election": election,
        "district": district,
        "proposals": proposals[:limit],
        "total": total,
        "count": len(proposals),
        "limit": limit,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def positions_by_text(request: HttpRequest):
    return await _filter_positions(request)


async def positions_by_election(request: HttpRequest, election_id: int):
    return await _filter_positions(request, limit=20, election_id=election_id)


async def positions_by_district(request: HttpRequest, district_id: int):
    return await _filter_positions(request, limit=20, district_id=district_id)


async def positions_by_election_and_district(
    request: HttpRequest, election_id: int, district_id: int
):
    return await _filter_positions(
        request, limit=20, election_id=election_id, district_id=district_id
    )


async def _filter_positions(
    request: HttpRequest, *, limit: int = 0, election_id: int = 0, district_id: int = 0
):
    q = request.GET.get("q", "").strip().lower()
    limit = int(request.GET.get("limit", limit))

    if election_id:
        election = await helpers.get_election(election_id)
    else:
        election = None

    if district_id:
        district = await helpers.get_district(district_id)
    else:
        district = None

    total, positions = await helpers.get_positions(
        q, limit, election_id=election_id, district_id=district_id
    )

    context = {
        "q": q,
        "election": election,
        "district": district,
        "positions": positions[:limit],
        "total": total,
        "count": len(positions),
        "limit": limit,
    }

    if "limit" in request.GET:
        template_name = "explore/_positions.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)
