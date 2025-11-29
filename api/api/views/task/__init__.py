from rest_framework import permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from api.views.task import serializers
from task.models import OfflineTask
from source.models import ScrapedRecord
from api.mixins import CreateMix



class OfflineTaskViewSet(CreateMix):
    queryset = OfflineTask.objects.filter(parent_task__isnull=True)
    serializer_class = serializers.OfflineTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        data["user_added"] = request.user.id
        serializer = serializers.OfflineTaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivityView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from task.api.activity import BuildSpendGroups
        from django.utils import timezone
        from datetime import timedelta
        from django.contrib.auth.models import User

        days_ago = request.query_params.get("days_ago", 60)
        user_id = request.query_params.get("user_id", None)
        worker_user = request.user

        if user_id and worker_user.profile.is_manager:
            worker_user = User.objects.get(id=user_id)
        now = timezone.now()
        last_days = now - timedelta(days=int(days_ago))
        tasks = worker_user.async_tasks\
            .filter(date_start__gte=last_days, parent_task__isnull=True)\
            .prefetch_related("task_function")
        tasks_data = serializers.AsyncTaskActivitySerializer(
            tasks, many=True).data
        clicks = worker_user.clicks.filter(date__gte=last_days)
        clicks_data = serializers.ClickHistoryActivitySerializer(
            clicks, many=True).data
        offline = worker_user.offline_tasks.filter(date_start__gte=last_days)
        offline_data = serializers.OfflineTaskActivitySerializer(
            offline, many=True).data
        activities = tasks_data + clicks_data + offline_data
        activities.sort(key=lambda x: x["real_start"], reverse=False)
        all_activities, spend_groups = BuildSpendGroups(activities).build_spend_groups()
        data = {
            "activities": activities,
            "spend_groups": spend_groups,
        }
        return Response(data, status=status.HTTP_200_OK)
