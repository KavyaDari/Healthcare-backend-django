from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from .models import Doctor
from .serializers import DoctorSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Doctors'],
        summary='List doctors',
        description='List all doctor records. Supports filtering by specialization and searching by name or specialization.',
        parameters=[
            OpenApiParameter(
                name='specialization',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter doctors by specialization (case-insensitive substring match).'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Search doctors by name or specialization (case-insensitive substring match).'
            ),
        ]
    ),
    create=extend_schema(tags=['Doctors'], summary='Add doctor', description='Create a new doctor profile.'),
    retrieve=extend_schema(tags=['Doctors'], summary='Retrieve doctor', description='Retrieve details of a doctor profile by ID.'),
    update=extend_schema(tags=['Doctors'], summary='Update doctor', description='Fully update a doctor profile.'),
    partial_update=extend_schema(tags=['Doctors'], summary='Partially update doctor', description='Partially update a doctor profile.'),
    destroy=extend_schema(tags=['Doctors'], summary='Delete doctor', description='Delete a doctor profile.'),
)
class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Doctor.objects.all().order_by('id')
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request, 'query_params'):
            return queryset

        specialization = self.request.query_params.get('specialization')
        search = self.request.query_params.get('search')

        if specialization and specialization.strip():
            queryset = queryset.filter(specialization__icontains=specialization.strip())
        if search and search.strip():
            term = search.strip()
            queryset = queryset.filter(
                Q(name__icontains=term) | Q(specialization__icontains=term)
            )

        return queryset