from django.db import IntegrityError
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from .models import PatientDoctorMapping
from .serializers import MappingSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Mappings'],
        summary='List patient-doctor mappings',
        description='List mappings for patients owned by the authenticated user (or all mappings for staff users). Supports filtering by patient_id and doctor_id.',
        parameters=[
            OpenApiParameter(
                name='patient_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter mappings by patient ID (must be a valid integer).'
            ),
            OpenApiParameter(
                name='doctor_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter mappings by doctor ID (must be a valid integer).'
            ),
        ]
    ),
    create=extend_schema(tags=['Mappings'], summary='Create mapping', description='Map an eligible patient owned by the authenticated user to a doctor. Duplicate mappings are rejected.'),
    retrieve=extend_schema(tags=['Mappings'], summary='Retrieve mapping', description='Retrieve details of a patient-doctor mapping.'),
    update=extend_schema(tags=['Mappings'], summary='Update mapping', description='Fully update a patient-doctor mapping.'),
    partial_update=extend_schema(tags=['Mappings'], summary='Partially update mapping', description='Partially update a patient-doctor mapping.'),
    destroy=extend_schema(tags=['Mappings'], summary='Delete mapping', description='Delete a patient-doctor mapping.'),
)
class MappingViewSet(viewsets.ModelViewSet):
    serializer_class = MappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return PatientDoctorMapping.objects.none()

        if self.request.user.is_staff:
            queryset = PatientDoctorMapping.objects.all()
        else:
            queryset = PatientDoctorMapping.objects.filter(patient__user=self.request.user)

        queryset = queryset.select_related('patient', 'doctor')

        patient_id = self.request.query_params.get('patient_id')
        doctor_id = self.request.query_params.get('doctor_id')

        if patient_id:
            try:
                patient_pk = int(patient_id)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"patient_id": "Must be a valid integer."})
            queryset = queryset.filter(patient_id=patient_pk)

        if doctor_id:
            try:
                doctor_pk = int(doctor_id)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"doctor_id": "Must be a valid integer."})
            queryset = queryset.filter(doctor_id=doctor_pk)

        return queryset.order_by('-assigned_at')

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["This patient is already mapped to this doctor."]}
            )

    def perform_update(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["This patient is already mapped to this doctor."]}
            )