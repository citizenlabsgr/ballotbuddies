from django.http import HttpRequest
from django.shortcuts import render

from asgiref.sync import sync_to_async

from . import helpers

async_render = sync_to_async(render)


async def index(request: HttpRequest):
    limit = int(request.GET.get("limit", 20))

    proposals = await helpers.get_proposals(limit)

    context = {
        "proposals": proposals[:limit],
        "count": len(proposals),
        "limit": limit,
        "step": 20,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def by_election(request: HttpRequest, election_id: int):
    limit = int(request.GET.get("limit", 20))

    election = await helpers.get_election(election_id)
    proposals = await helpers.get_proposals(limit, election_id=election_id)

    context = {
        "election": election,
        "proposals": proposals[:limit],
        "count": len(proposals),
        "limit": limit,
        "step": 20,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)


async def by_district(request: HttpRequest, district_id: int):
    limit = int(request.GET.get("limit", 20))

    district = await helpers.get_district(district_id)
    proposals = await helpers.get_proposals(limit, district_id=district_id)

    context = {
        "district": district,
        "proposals": proposals[:limit],
        "count": len(proposals),
        "limit": limit,
        "step": 20,
    }

    if "limit" in request.GET:
        template_name = "explore/_proposals.html"
    else:
        template_name = "explore/index.html"

    return await async_render(request, template_name, context)
