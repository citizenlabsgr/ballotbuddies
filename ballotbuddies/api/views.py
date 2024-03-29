from django.shortcuts import get_object_or_404

import log
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ballotbuddies.buddies.models import Voter


class VoterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    referrer = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    birth_date = serializers.DateField()
    zip_code = serializers.CharField()


class BallotSerializer(serializers.Serializer):
    voter = serializers.CharField(max_length=200)
    url = serializers.URLField()


@api_view(["POST"])
def provision_voter(request):
    serializer = VoterSerializer(data=request.POST)
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, 400)

    voter = Voter.objects.from_email(
        serializer.validated_data["email"], serializer.validated_data["referrer"]
    )
    if voter.complete:
        message = "Found voter."
    else:
        voter.user.update_name(  # type: ignore
            request,
            serializer.validated_data["first_name"],
            serializer.validated_data["last_name"],
        )
        voter.birth_date = serializer.validated_data["birth_date"]
        voter.zip_code = serializer.validated_data["zip_code"]
        voter.save()
        message = "Created voter."

    return Response({"message": message})


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
