from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Patient
from .serializers import PatientSerializer


@extend_schema_view(
    list=extend_schema(tags=['Patients'], summary='List patients', description='List all patients owned by the authenticated user (or all patients for staff users).'),
    create=extend_schema(tags=['Patients'], summary='Create patient', description='Create a new patient record. The owner is automatically assigned to the authenticated user.'),
    retrieve=extend_schema(tags=['Patients'], summary='Retrieve patient', description='Retrieve details of a patient owned by the authenticated user (or any for staff).'),
    update=extend_schema(tags=['Patients'], summary='Update patient', description='Fully update a patient record owned by the authenticated user.'),
    partial_update=extend_schema(tags=['Patients'], summary='Partially update patient', description='Partially update a patient record owned by the authenticated user.'),
    destroy=extend_schema(tags=['Patients'], summary='Delete patient', description='Delete a patient record owned by the authenticated user.'),
)
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Patient.objects.none()
        if self.request.user.is_staff:
            return Patient.objects.all().order_by('id')
        return Patient.objects.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)