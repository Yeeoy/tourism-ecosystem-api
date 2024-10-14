from django.contrib.auth import (get_user_model, authenticate)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()  # Get the user model
        fields = ['id', 'email', 'password', 'name', 'is_staff', 'is_active']  # Fields to be serialized
        # Additional keyword arguments
        extra_kwargs = {
            'password': {
                'write_only': True,  # Password field is write-only
                'min_length': 5  # Minimum length for the password is 5
            }
        }

    # Create user
    def create(self, validated_data):
        # Create a user using the validated data
        return get_user_model().objects.create_user(**validated_data)

    # Update user
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)  # Remove password from validated data
        user = super().update(instance, validated_data)  # Update other fields of the user

        if password:
            user.set_password(password)  # Set new password
            user.save()  # Save the user

        return user  # Return the updated user


# Authentication token serializer
class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()  # Email field
    password = serializers.CharField(
        style={'input_type': 'password'},  # Input type for the password field is password
        trim_whitespace=False  # Do not trim whitespace
    )

    # Validation method
    def validate(self, attrs):
        email = attrs.get('email')  # Get email
        password = attrs.get('password')  # Get password

        user = authenticate(
            request=self.context.get('request'),  # Get request context
            username=email,  # Use email as username
            password=password  # Use provided password
        )

        if not user:
            # Unable to authenticate with provided credentials
            msg = _('Unable to authenticate with provided credentials')
            # Raise validation error
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user  # Add user to validated data
        return attrs  # Return validated data
