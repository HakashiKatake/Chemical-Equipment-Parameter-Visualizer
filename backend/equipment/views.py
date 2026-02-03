"""
API Views for Chemical Equipment Parameter Visualizer
"""
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Dataset, Equipment
from .serializers import (
    DatasetSerializer, DatasetDetailSerializer, 
    EquipmentSerializer, CSVUploadSerializer
)
from .csv_normalizer import CSVNormalizer, CSVValidationError
from .analytics import compute_analytics
from .reports import generate_pdf_report


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'},
                },
                'required': ['username', 'password']
            }
        },
        responses={200: {'type': 'object', 'properties': {'token': {'type': 'string'}}}}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def login(self, request):
        """Login and get authentication token"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username
            })
        
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'},
                    'email': {'type': 'string'},
                },
                'required': ['username', 'password', 'email']
            }
        },
        responses={201: {'type': 'object', 'properties': {'token': {'type': 'string'}}}}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def register(self, request):
        """Register a new user"""
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email or ''
        )
        
        token = Token.objects.create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for dataset management.
    Provides list and detail views for user datasets.
    """
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return datasets for current user only"""
        return Dataset.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return DatasetDetailSerializer
        return DatasetSerializer
    
    @extend_schema(
        request=CSVUploadSerializer,
        responses={
            201: DatasetDetailSerializer,
            400: {'description': 'Validation errors'}
        }
    )
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload and process a CSV file.
        
        The CSV will be validated, normalized, and stored.
        Automatically maintains last 5 datasets per user.
        """
        serializer = CSVUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        csv_file = serializer.validated_data['file']
        
        try:
            # Read and normalize CSV
            file_content = csv_file.read()
            normalized_data = CSVNormalizer.validate_and_normalize(file_content)
            
            # Create dataset and equipment records in a transaction
            with transaction.atomic():
                dataset = Dataset.objects.create(
                    user=request.user,
                    filename=csv_file.name,
                    row_count=len(normalized_data)
                )
                
                # Bulk create equipment records
                equipment_objects = [
                    Equipment(dataset=dataset, **item)
                    for item in normalized_data
                ]
                Equipment.objects.bulk_create(equipment_objects)
            
            # Return created dataset with equipment
            response_serializer = DatasetDetailSerializer(dataset)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except CSVValidationError as e:
            return Response(
                {'errors': e.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        responses={200: {'type': 'object', 'additionalProperties': True}}
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """
        Get complete analytics for a dataset.
        
        Returns:
        - summary: Global statistics
        - type_distribution: Equipment count by type
        - histogram: Flowrate histogram data
        - scatter: Pressure vs Temperature scatter data
        - table: Complete equipment data
        """
        dataset = self.get_object()
        equipment_qs = dataset.equipment.all()
        
        analytics_data = compute_analytics(equipment_qs)
        
        return Response(analytics_data)
    
    @extend_schema(
        responses={200: {'description': 'PDF file', 'content': {'application/pdf': {}}}}
    )
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """
        Generate and download PDF report for a dataset.
        
        Report includes:
        - Dataset metadata
        - Summary statistics
        - Charts (histogram, scatter, type distribution)
        - Complete data table
        """
        dataset = self.get_object()
        equipment_qs = dataset.equipment.all()
        
        # Compute analytics
        analytics_data = compute_analytics(equipment_qs)
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(dataset, analytics_data)
        
        from django.http import HttpResponse
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{dataset.filename}_{dataset.id}.pdf"'
        
        return response


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for equipment records.
    Read-only access to equipment data.
    """
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return equipment for current user's datasets only"""
        return Equipment.objects.filter(dataset__user=self.request.user)
