from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction, IntegrityError
from django.utils.html import escape
import secrets
import re

from Users.models import User
from Parent.models import Parent
from Student.models import Student


# ====================
# Custom Related Field
# ====================
class ParentUserPKRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Accept a list of *User* IDs (role='parent') from the client,
    but convert them to Parent instances for Student.parents.
    Also represent them back to the client as User IDs.
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('many', True)
        # Internally we relate to Parent, not User
        kwargs.setdefault('queryset', Parent.objects.select_related('user').all())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            parent = Parent.objects.select_related('user').get(user_id=data)
        except Parent.DoesNotExist:
            raise serializers.ValidationError("Invalid parent user ID.")
        return parent

    def to_representation(self, value):
        return value.user_id  # return parent’s user ID


# ====================
# USER SERIALIZER
# ====================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    confirm_password = serializers.CharField(write_only=True, required=False, max_length=128)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'password', 'confirm_password', 'is_active', 'is_staff', 'date_joined', 'role'
        ]
        read_only_fields = ['id', 'date_joined', 'is_staff']
        extra_kwargs = {
            'email': {'required': True, 'max_length': 254},
            'first_name': {'required': True, 'max_length': 50},
            'last_name': {'required': True, 'max_length': 50},
        
        }

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        value = escape(value.strip().lower())
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email format.")
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        value = value.strip()
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "First name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        return value.title()

    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        value = value.strip()
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "Last name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        return value.title()

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password and confirm_password is not None and password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                validated_data.pop('confirm_password', None)
                password = validated_data.pop('password')
                validated_data.setdefault('username', f"user_{secrets.token_urlsafe(12)}")
                validated_data.setdefault('role', 'parent')
                user = User(**validated_data)
                user.set_password(password)
                user.save()
                return user
        except IntegrityError:
            raise serializers.ValidationError({
                "error": "User creation failed. Please try again."
            })

    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ====================
# STUDENT SERIALIZER
# ====================
class StudentSerializer(serializers.ModelSerializer):
    parent_users = ParentUserPKRelatedField(
        source='parents',
        help_text="List of parent *User* IDs"
    )

    class Meta:
        model = Student
        fields = [
            'student_id', 'first_name', 'last_name',
            'current_class', 'is_active', 'parent_users',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['student_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'first_name': {'max_length': 50},
            'last_name': {'max_length': 50},
            'current_class': {'max_length': 50},
        }

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        value = value.strip()
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "First name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        return value.title()

    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        value = value.strip()
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "Last name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        return value.title()

    def validate_current_class(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Current class is required.")
        return value.strip()

    def validate_parent_users(self, value):
        if not value:
            raise serializers.ValidationError("At least one parent must be assigned.")
        if len(value) > 4:
            raise serializers.ValidationError("A student cannot have more than 4 parents/guardians.")
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                parents = validated_data.pop('parents', [])
                student = Student.objects.create(**validated_data)
                student.parents.set(parents)
                return student
        except IntegrityError:
            raise serializers.ValidationError({
                "error": "Student creation failed. Please try again."
            })

    def update(self, instance, validated_data):
        parents = validated_data.pop('parents', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if parents is not None:
            instance.parents.set(parents)
        instance.save()
        return instance


# ====================
# REGISTER SERIALIZER
# ====================
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with role-based creation.
    Handles user creation with password validation and confirmation.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        max_length=128,
        style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'password', 'confirm_password'
        ]
        extra_kwargs = {
            'email': {'required': True, 'max_length': 254},
            'first_name': {'required': True, 'max_length': 100},
            'last_name': {'required': True, 'max_length': 100},
            'phone_number': {'required': False, 'max_length': 15},
        }

    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        value = escape(value.strip().lower())
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email format.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        """Validate password strength using Django's validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_first_name(self, value):
        """Validate first name format."""
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        value = value.strip()
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "First name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        return value.title()

    def validate_last_name(self, value):
        """Validate last name format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        value = value.strip()
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "Last name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        return value.title()

    def validate_phone_number(self, value):
        """Validate phone number format if provided."""
        if value:
            value = escape(value.strip())
            digits_only = re.sub(r'\D', '', value)
            if len(digits_only) < 10:
                raise serializers.ValidationError("Phone number must have at least 10 digits.")
            if len(digits_only) > 15:
                raise serializers.ValidationError("Phone number cannot have more than 15 digits.")
            if User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate(self, attrs):
        """Validate password confirmation and other cross-field validations."""
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        """Create a new user with the validated data."""
        try:
            with transaction.atomic():
                # Remove confirm_password as it's not needed for user creation
                validated_data.pop('confirm_password', None)

                # Extract password for separate handling
                password = validated_data.pop('password')

               
                # Create user instance
                user = User(**validated_data)
                user.set_password(password)
                user.save()

                return user
        except IntegrityError:
            raise serializers.ValidationError({
                "error": "User registration failed. Please try again."
            })


# ====================
# PARENT SERIALIZER
# ====================
class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Parent
        fields = [
            'id', 'user', 'phone_number', 'verified', 'is_primary',
            'created_at', 'updated_at', 'full_name', 'display_phone', 'total_children'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'full_name',
            'display_phone', 'total_children'
        ]
        extra_kwargs = {
            'phone_number': {'required': True, 'max_length': 12},
        }

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        value = escape(value.strip())
        digits_only = re.sub(r'\D', '', value)
        if len(digits_only) < 10:
            raise serializers.ValidationError("Phone number must have at least 10 digits.")
        if len(digits_only) > 15:
            raise serializers.ValidationError("Phone number cannot have more than 15 digits.")
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user_data = validated_data.pop('user')
                user_data['role'] = 'parent'
                if 'password' in user_data:
                    user_data['confirm_password'] = user_data['password']
                user_serializer = UserSerializer(data=user_data)
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()
                parent = Parent.objects.create(user=user, **validated_data)
                return parent
        except IntegrityError:
            raise serializers.ValidationError({
                "error": "Parent creation failed. Please try again."
            })

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
