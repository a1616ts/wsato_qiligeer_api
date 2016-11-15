from rest_framework import serializers


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=256, required=False)

class ResultSerializer(serializers.Serializer):
    result = serializers.CharField(max_length=256, required=False)
