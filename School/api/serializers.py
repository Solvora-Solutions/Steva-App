from rest_framework import serializers
from django.db import IntegrityError
from Users.models import User
from Parent.models import Parent
from Student.models import Student
from Staff.models import Staff


# ====================
# BASIC CHILD SERIALIZER
# ====================
class ChildDisplaySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'full_name']

    def get_full_name(self, obj):
        first = obj.user.first_name if obj.user else ''
        last = obj.user.last_name if obj.user else ''
        return f"{first} {last}".strip()


# ====================
# USER SERIALIZER
# ====================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        try:
            password = validated_data.pop('password', None)
            if not password:
                raise serializers.ValidationError({"password": "Password is required."})

            validated_data['role'] = validated_data.get('role', 'parent')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except IntegrityError as e:
            raise serializers.ValidationError({"error": "User creation failed.", "details": str(e)})
        except Exception as e:
            raise serializers.ValidationError({"error": "Unexpected error while creating user.", "details": str(e)})


# ====================
# STUDENT SERIALIZER (FULL — READ-ONLY via ViewSet)
# ====================
class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_full_name(self, obj):
        first = obj.user.first_name if obj.user else ''
        last = obj.user.last_name if obj.user else ''
        return f"{first} {last}".strip()


# ====================
# STAFF SERIALIZER
# ====================
class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


# ====================
# PARENT SERIALIZER
# ====================
class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    children = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True)

    class Meta:
        model = Parent
        fields = ['id', 'user', 'phone_number', 'address', 'occupation', 'children']
        read_only_fields = ['id']

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Enter a valid phone number (at least 10 digits).")
        return value

    def validate_occupation(self, value):
        if not value.strip():
            raise serializers.ValidationError("Occupation cannot be blank.")
        return value

    def create(self, validated_data):
        try:
            user_data = validated_data.pop('user')
            children_data = validated_data.pop('children', [])

            user_data['role'] = 'parent'
            user = UserSerializer().create(user_data)

            parent = Parent.objects.create(user=user, **validated_data)
            parent.children.set(children_data)
            return parent
        except IntegrityError as e:
            raise serializers.ValidationError({"error": "Parent creation failed.", "details": str(e)})
        except Exception as e:
            raise serializers.ValidationError({"error": "Unexpected error while creating parent.", "details": str(e)})

    def update(self, instance, validated_data):
        try:
            user_data = validated_data.pop('user', None)
            children = validated_data.pop('children', None)

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

            if children is not None:
                instance.children.set(children)

            return instance
        except IntegrityError as e:
            raise serializers.ValidationError({"error": "Parent update failed.", "details": str(e)})
        except Exception as e:
            raise serializers.ValidationError({"error": "Unexpected error while updating parent.", "details": str(e)})

    def to_representation(self, instance):
        try:
            rep = super().to_representation(instance)
            rep['user'] = UserSerializer(instance.user).data
            rep['children'] = ChildDisplaySerializer(instance.children.all(), many=True).data
            return rep
        except Exception as e:
            return {"error": "Failed to serialize parent data", "details": str(e)}
