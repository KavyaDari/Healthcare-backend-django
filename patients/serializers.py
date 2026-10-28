from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'user', 'name', 'age', 'gender', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Patient name cannot be blank.")
        return name

    def validate_age(self, value):
        if value < 0:
            raise serializers.ValidationError("Age cannot be negative.")
        if value > 130:
            raise serializers.ValidationError("Age must be realistic (130 or less).")
        return value

    def validate_gender(self, value):
        gender = value.strip()
        if not gender:
            raise serializers.ValidationError("Gender cannot be blank.")
        return gender