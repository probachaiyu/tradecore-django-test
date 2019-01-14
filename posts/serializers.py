
from posts import services
from posts.models import Post


from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


class FanSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'full_name',
        )

    def get_full_name(self, obj):
        return obj.get_full_name()


class PostSerializerSchema(serializers.ModelSerializer):
    is_fan = serializers.SerializerMethodField()
    author = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'author',
            'body',
            'is_fan',
            'total_likes',
        )

    def get_is_fan(self, obj) -> bool:
        """Check if a `request.user` has liked this tweet (`obj`).
        """
        user = self.context.get('request').user
        return services.is_fan(obj, user)

    def create(self, validated_data):
        validated_data["author"] = self.context.get('request').user
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance