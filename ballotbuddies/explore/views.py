from django.http import HttpRequest
from django.shortcuts import render

from asgiref.sync import sync_to_async

from . import helpers

async_render = sync_to_async(render)


async def index(request: HttpRequest):
    proposals = await helpers.get_proposals()
    context = {"proposals": proposals}
    return await async_render(request, "explore/index.html", context)


async def by_election(request: HttpRequest, election_id: int):
    election = await helpers.get_election(election_id)
    proposals = await helpers.get_proposals(election_id=election_id)
    context = {"election": election, "proposals": proposals}
    return await async_render(request, "explore/index.html", context)


async def by_district(request: HttpRequest, district_id: int):
    district = await helpers.get_district(district_id)
    proposals = await helpers.get_proposals(district_id=district_id)
    context = {"district": district, "proposals": proposals}
    return await async_render(request, "explore/index.html", context)
