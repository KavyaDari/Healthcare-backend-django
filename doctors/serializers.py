from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'specialization', 'experience']
        read_only_fields = ['id']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Doctor name cannot be blank.")
        return name

    def validate_specialization(self, value):
        spec = value.strip()
        if not spec:
            raise serializers.ValidationError("Specialization cannot be blank.")
        return spec

    def validate_experience(self, value):
        if value < 0:
            raise serializers.ValidationError("Experience cannot be negative.")
        if value > 75:
            raise serializers.ValidationError("Experience must be realistic (75 years or less).")
        return value