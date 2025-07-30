from rest_framework import serializers
from django.db import IntegrityError
import uuid
from Users.models import User
from Parent.models import Parent
from Student.models import Student


# ====================
# CHILD DISPLAY SERIALIZER
# ====================
class ChildDisplaySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['student_id', 'full_name']  # ✅ Show student_id

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# ====================
# USER SERIALIZER
# ====================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        try:
            password = validated_data.pop('password')
            validated_data.setdefault('username', str(uuid.uuid4())[:8])  # Auto username if missing
            validated_data['role'] = validated_data.get('role', 'parent')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except IntegrityError:
            raise serializers.ValidationError({"error": "User creation failed. Email might already exist."})


# ====================
# STUDENT SERIALIZER
# ====================
class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    parents = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Parent.objects.all()
    )

    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'current_class', 'is_active', 'parents', 'full_name']
        read_only_fields = ['student_id']  # ✅ Prevent manual setting

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def validate_parents(self, value):
        if not value:
            raise serializers.ValidationError("At least one parent must be assigned.")
        return value


# ====================
# PARENT SERIALIZER
# ====================
class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    children = ChildDisplaySerializer(source='students', many=True, read_only=True)

    class Meta:
        model = Parent
        fields = ['id', 'user', 'phone_number', 'created_at', 'verified', 'children']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        try:
            user_data = validated_data.pop('user')
            user_data['role'] = 'parent'
            user = UserSerializer().create(user_data)
            parent = Parent.objects.create(user=user, **validated_data)
            return parent
        except IntegrityError:
            raise serializers.ValidationError({"error": "Parent creation failed. Email or phone number might already exist."})

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
