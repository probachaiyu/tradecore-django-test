from django.contrib.auth import get_user_model
import re
from django.conf import settings
from marshmallow import fields
from email_hunter import EmailHunterClient
from rest_framework import serializers
from users.clearbit_client import ClearbitClient

hunter = EmailHunterClient(settings.EMAIL_HUNTER_API_KEY)
User = get_user_model()

class TokenSerializer(serializers.Serializer):
    """
    This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "date_of_birth",
                  "bio", "location", "facebook", "avatar",
                  "site", "linkedin", "skype")



class UpdateUserSchema(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "date_of_birth",
                  "bio", "location", "facebook", "avatar",
                  "site", "linkedin", "skype")

    def validate_email(cls, key):
        is_exists, result = hunter.exist(key)
        if not is_exists:
            raise serializers.ValidationError("Email address is not found in emailhunter.co %s" % key)
        return key

    def validate_password(cls, key):
        if not re.match(
                r"^.*(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}.*$", key
                ):
            raise serializers.ValidationError("Invalid password: %s" % key)
        return key

    def create(self, validated_data):
        clearbit_data = ClearbitClient.get_person_data(validated_data["email"])
        print('===', clearbit_data)
        result = ClearbitClient.update_person_data(clearbit_data, validated_data)
        return User.objects.create(**result)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class CreateUserSchema(UpdateUserSchema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.String(required=True)

class LoginUserSchema(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')