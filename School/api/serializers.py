from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction, IntegrityError
import uuid
import re

from Users.models import User
from Parent.models import Parent
from Student.models import Student


# ====================
# USER SERIALIZER
# ====================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'password', 'confirm_password', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email format.")
        
        # Check uniqueness (excluding current instance for updates)
        queryset = User.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value.lower().strip()

    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_first_name(self, value):
        """Validate first name"""
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError("First name can only contain letters, spaces, hyphens, apostrophes, and periods.")
        
        return value.strip().title()

    def validate_last_name(self, value):
        """Validate last name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError("Last name can only contain letters, spaces, hyphens, apostrophes, and periods.")
        
        return value.strip().title()

    def validate(self, attrs):
        """Cross-field validation"""
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        # Only validate password confirmation during creation or when password is being changed
        if password and confirm_password is not None:
            if password != confirm_password:
                raise serializers.ValidationError({
                    'confirm_password': 'Passwords do not match.'
                })
        
        return attrs

    def create(self, validated_data):
        """Create user with proper error handling"""
        try:
            with transaction.atomic():
                # Remove confirm_password as it's not needed for creation
                validated_data.pop('confirm_password', None)
                
                password = validated_data.pop('password')
                
                # Generate username if not provided
                validated_data.setdefault('username', str(uuid.uuid4())[:8])
                
                # Set default role
                validated_data.setdefault('role', 'parent')
                
                user = User(**validated_data)
                user.set_password(password)
                user.save()
                return user
                
        except IntegrityError as e:
            raise serializers.ValidationError({
                "error": "User creation failed. Email or username might already exist."
            })

    def update(self, instance, validated_data):
        """Update user with proper password handling"""
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
    parents = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Parent.objects.all(),
        help_text="List of parent IDs"
    )

    class Meta:
        model = Student
        fields = [
            'student_id', 'first_name', 'last_name', 
            'current_class', 'is_active', 'parents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['student_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'current_class': {'required': True},
        }

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError("First name can only contain letters, spaces, hyphens, apostrophes, and periods.")
        
        return value.strip().title()

    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError("Last name can only contain letters, spaces, hyphens, apostrophes, and periods.")
        
        return value.strip().title()

    def validate_current_class(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Current class is required.")
        return value.strip()

    def validate_parents(self, value):
        if not value:
            raise serializers.ValidationError("At least one parent must be assigned.")
        
        if len(value) > 4:  # Reasonable limit
            raise serializers.ValidationError("A student cannot have more than 4 parents/guardians.")
        
        return value

    def create(self, validated_data):
        """Create student with proper many-to-many handling"""
        try:
            with transaction.atomic():
                parents = validated_data.pop('parents', [])
                student = Student.objects.create(**validated_data)
                student.parents.set(parents)
                return student
        except IntegrityError:
            raise serializers.ValidationError({
                "error": "Student creation failed. Student ID might already exist."
            })

    def update(self, instance, validated_data):
        """Update student with proper many-to-many handling"""
        parents = validated_data.pop('parents', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if parents is not None:
            instance.parents.set(parents)
        
        instance.save()
        return instance


# ====================
# PARENT SERIALIZER
# ====================
class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Parent
        fields = [
            'id', 'user', 'phone_number', 'address', 'emergency_contact',
            'created_at', 'verified'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'phone_number': {'required': True},
        }

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', value)
        
        if len(digits_only) < 10:
            raise serializers.ValidationError("Phone number must have at least 10 digits.")
        
        if len(digits_only) > 15:
            raise serializers.ValidationError("Phone number cannot have more than 15 digits.")
        
        return value.strip()

    def validate_address(self, value):
        """Validate address"""
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Address must be at least 5 characters long.")
        return value.strip() if value else ""

    def create(self, validated_data):
        """Create parent with user in a transaction"""
        try:
            with transaction.atomic():
                user_data = validated_data.pop('user')
                user_data['role'] = 'parent'
                
                # Add confirm_password for validation if password is provided
                if 'password' in user_data:
                    user_data['confirm_password'] = user_data['password']
                
                user_serializer = UserSerializer(data=user_data)
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()
                
                parent = Parent.objects.create(user=user, **validated_data)
                return parent
                
        except IntegrityError:
            raise serializers.ValidationError({
                "error": "Parent creation failed. Email or phone number might already exist."
            })

    def update(self, instance, validated_data):
        """Update parent and associated user"""
        user_data = validated_data.pop('user', None)
        
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance