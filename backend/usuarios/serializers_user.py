from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "rol", "is_active", "password", "date_joined", "last_login"]
        read_only_fields = ["date_joined", "last_login"]

    def create(self, validated_data):
        pwd = validated_data.pop("password", None)
        user = User(**validated_data)
        user.set_password(pwd or User.objects.make_random_password())
        user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if pwd:
            instance.set_password(pwd)
        instance.save()
        return instance
