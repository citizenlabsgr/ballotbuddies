from django.http import HttpRequest
from django.shortcuts import render

from asgiref.sync import sync_to_async

from . import helpers

async_render = sync_to_async(render)


async def index(request: HttpRequest):
    q = request.GET.get("q", "").strip().lower()
    limit = int(request.GET.get("limit", 0))

    proposals = await helpers.get_proposals(q, limit)

    context = {
        "q": q,
        "proposals": proposals[:limit],
        "count": len(proposals),
        "limit": limit,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def by_election(request: HttpRequest, election_id: int):
    q = request.GET.get("q", "").strip().lower()
    limit = int(request.GET.get("limit", 20))

    election = await helpers.get_election(election_id)
    proposals = await helpers.get_proposals(q, limit, election_id=election_id)

    context = {
        "q": q,
        "election": election,
        "proposals": proposals[:limit],
        "count": len(proposals),
        "limit": limit,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def by_district(request: HttpRequest, district_id: int):
    q = request.GET.get("q", "").strip().lower()
    limit = int(request.GET.get("limit", 20))

    district = await helpers.get_district(district_id)
    proposals = await helpers.get_proposals(q, limit, district_id=district_id)

    context = {
        "q": q,
        "district": district,
        "proposals": proposals[:limit],
        "count": len(proposals),
        "limit": limit,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def by_election_and_district(
    request: HttpRequest, election_id: int, district_id: int
):
    q = request.GET.get("q", "").strip().lower()
    limit = int(request.GET.get("limit", 20))

    election = await helpers.get_election(election_id)
    district = await helpers.get_district(district_id)
    proposals = await helpers.get_proposals(
        q, limit, election_id=election_id, district_id=district_id
    )

    context = {
        "q": q,
        "election": election,
        "district": district,
        "proposals": proposals[:limit],
        "count": len(proposals),
        "limit": limit,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)
