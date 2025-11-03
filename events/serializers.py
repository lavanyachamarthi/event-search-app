from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "serialno",
            "version",
            "account_id",
            "instance_id",
            "srcaddr",
            "dstaddr",
            "protocol",
            "packets",
            "bytes",
            "starttime",
            "endtime",
            "action",
            "log_status",
            "srcport",
            "dstport",
            "file_name",
            "raw_line",
        )




