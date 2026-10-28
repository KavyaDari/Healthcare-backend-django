from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.name')
    doctor_name = serializers.ReadOnlyField(source='doctor.name')

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'patient_name', 'doctor_name', 'assigned_at']
        read_only_fields = ['id', 'assigned_at', 'patient_name', 'doctor_name']
        validators = [
            UniqueTogetherValidator(
                queryset=PatientDoctorMapping.objects.all(),
                fields=['patient', 'doctor'],
                message="This patient is already mapped to this doctor."
            )
        ]

    def validate_patient(self, patient):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated and not request.user.is_staff:
            if patient.user != request.user:
                raise serializers.ValidationError(
                    "You do not have permission to map this patient."
                )
        return patient

    def validate(self, attrs):
        request = self.context.get('request')
        patient = attrs.get('patient') or (self.instance.patient if self.instance else None)
        if patient and request and request.user and request.user.is_authenticated and not request.user.is_staff:
            if patient.user != request.user:
                raise serializers.ValidationError(
                    {"patient": "You do not have permission to map this patient."}
                )
        return attrs