from rest_framework import serializers
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("Username cannot be blank.")
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return username

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError("Email cannot be blank.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError("Password cannot be blank or entirely whitespace.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )