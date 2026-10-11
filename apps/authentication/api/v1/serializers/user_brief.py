from rest_framework import serializers


class UserBriefSerializer(serializers.Serializer):
    """سریالایزر خلاصه کاربر"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
    role_display = serializers.SerializerMethodField()

    def get_role_display(self, obj):
        return obj.get_role_display() if hasattr(obj, 'get_role_display') else obj.role