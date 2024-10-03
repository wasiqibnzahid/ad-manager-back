from rest_framework import serializers
from django.contrib.auth.models import User
from .models import NormalUserProfile, Report, Record

# Serializer for creating a normal user


class NormalUserSerializer(serializers.ModelSerializer):
    report_id = serializers.CharField(allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'report_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        report_id = validated_data.pop('report_id')
        is_admin = validated_data.pop('is_admin')
        user = User.objects.create_user(**validated_data)
        print(f"ASDASDASD AM EHE")
        NormalUserProfile.objects.create(user=user, report_id=report_id)
        return user


# Serializer for login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    from rest_framework import serializers


# Serializer for NormalUserProfile


class NormalUserProfileSerializer(serializers.ModelSerializer):
    # Get username from related User model
    username = serializers.CharField(source='user.username')
    is_admin = serializers.CharField(source='user.is_staff')

    class Meta:
        model = NormalUserProfile
        # Include fields you want to serialize
        fields = ['username', 'report_id', "id", "is_admin"]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        # or specify individual fields like ['id', 'name', 'status']
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        # or specify individual fields like ['id', 'name', 'status']
        fields = '__all__'
