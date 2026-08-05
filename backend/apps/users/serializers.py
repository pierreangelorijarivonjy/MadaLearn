from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User, UserRole, Role, Permission, RolePermission, UserStatus
from activity.models import ActivityLog


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'code', 'module', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True, source='role_permissions.permission')

    class Meta:
        model = Role
        fields = ('id', 'code', 'name', 'description', 'is_system', 'permissions', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.STUDENT)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'first_name', 'last_name', 'password', 'role', 'status', 'created_at')
        read_only_fields = ('id', 'created_at', 'status')

    def validate_role(self, value):
        return str(value).upper()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', UserRole.STUDENT)
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    delete_profile_photo = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'role', 'status', 'is_active', 'profile_photo', 'bio', 'last_login',
            'delete_profile_photo',
            'created_at', 'updated_at', 'deleted_at'
        )
        read_only_fields = ('id', 'username', 'created_at', 'updated_at', 'deleted_at', 'last_login')

    def get_role(self, obj):
        return str(obj.role or '').upper()

    def update(self, instance, validated_data):
        if validated_data.pop('delete_profile_photo', False):
            instance.profile_photo = None

        profile_photo = validated_data.get('profile_photo', None)
        if profile_photo == '':
            instance.profile_photo = None
            validated_data.pop('profile_photo', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = str(user.role or '').upper()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Include serializer context so ImageField can build absolute URLs
        data['user'] = UserProfileSerializer(self.user, context=self.context).data
        request = self.context.get('request')
        if request is not None:
            ActivityLog.objects.create(
                user=self.user,
                action='login',
                module='auth',
                description=f"Connexion utilisateur {self.user.username}",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        return data


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'role', 'status', 'is_active', 'profile_photo', 'bio', 'password',
            'created_at', 'updated_at', 'deleted_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')

    def get_role(self, obj):
        return str(obj.role or '').upper()

    def validate_role(self, value):
        return str(value).upper()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField(required=True)

    def validate_avatar(self, value):
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("L'image ne doit pas dépasser 2 Mo.")
        return value
