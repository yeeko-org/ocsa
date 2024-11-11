from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.views.note.serializers import (
    MentionSerializer, MentionMegaFullSerializer,
    ParticipantSimpleSerializer, InterestSerializer,
    InvolvedSerializer, StatusHistorySerializer)
from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantSerializer)

from source.models import Mention, StatusHistory
from actor.models import Participant, Interest
from impact.models import Impact
from event.models import Involved


class MentionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Mention.objects.all()

    serializer_class = MentionSerializer

    def common(self, request, serializer):

        if serializer.is_valid():
            serializer.save()

            new_serializer = MentionMegaFullSerializer(
                serializer.instance)
            return Response(
                new_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        return self.common(request, serializer)

    def update(self, request, *args, **kwargs):

        mention = self.get_object()
        serializer = self.get_serializer(mention, data=request.data)
        return self.common(request, serializer)


class ParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Participant.objects.all()

    serializer_class = ParticipantSimpleSerializer

    def create(self, request, *args, **kwargs):

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            new_serializer = ParticipantSerializer(
                serializer.instance)
            return Response(
                new_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImpactViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Impact.objects.all()

    serializer_class = ImpactSerializer


class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Interest.objects.all()

    serializer_class = InterestSerializer


class InvolvedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Involved.objects.all()

    serializer_class = InvolvedSerializer


class StatusHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = StatusHistory.objects.all()

    serializer_class = StatusHistorySerializer

