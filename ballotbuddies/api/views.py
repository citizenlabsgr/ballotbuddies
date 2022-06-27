from django.shortcuts import get_object_or_404

import log
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ballotbuddies.buddies.models import Voter


class BallotSerializer(serializers.Serializer):
    voter = serializers.CharField(max_length=200)
    url = serializers.URLField()


@api_view(["POST"])
def update_ballot(request):
    serializer = BallotSerializer(data=request.POST)
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, 400)

    slug = serializer.validated_data["voter"]
    ballot = serializer.validated_data["url"]
    voter: Voter = get_object_or_404(Voter, slug=slug)

    log.info(f"Updating {voter} ballot from {voter.ballot} to {ballot}")
    voter.ballot = ballot
    voter.save()
    return Response({"message": "Successfully updated voter's ballot."})
