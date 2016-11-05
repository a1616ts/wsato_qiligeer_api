from rest_framework import serializers


class CreateVmSerializer(serializers.Serializer):
    str = serializers.CharField(max_length=256, required=False)
