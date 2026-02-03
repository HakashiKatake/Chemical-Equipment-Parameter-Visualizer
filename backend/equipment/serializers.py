"""
Serializers for Equipment API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, Equipment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    equipment_count = serializers.IntegerField(source='row_count', read_only=True)
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'equipment_count']


class DatasetDetailSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    equipment_count = serializers.IntegerField(source='row_count', read_only=True)
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'equipment_count', 'equipment']


class CSVUploadSerializer(serializers.Serializer):
    """Serializer for CSV file upload"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validate file extension"""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError('File must be a CSV')
        return value
