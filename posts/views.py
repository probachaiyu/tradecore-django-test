from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings

# Get the JWT settings
from django_rest_network.permissions import IsOwner
from posts import services
from posts.mixins import LikedMixin
from posts.models import Post
from posts.serializers import PostSerializerSchema

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class ListCreatePostView(LikedMixin, generics.ListCreateAPIView):
    """
    GET post/
    POST post/
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializerSchema
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = PostSerializerSchema(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                    )
        else:
            return Response(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                    )


class PostDetailView(LikedMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET post/:id/
    PUT post/:id/
    DELETE post/:id/
    """
    queryset = Post.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwner)
    serializer_class = PostSerializerSchema

    def get(self, request, *args, **kwargs):
        try:
            post = self.queryset.get(pk=kwargs["pk"])
            if kwargs.get("slug") and kwargs["slug"] == "vote":
                if services.is_fan(post, request.user):
                    self.unlike(request, kwargs["pk"])
                else:
                    self.like(request, kwargs["pk"])
            return Response(PostSerializerSchema(post, context={"request": request}).data)
        except Post.DoesNotExist:
            return Response(
                    data={
                        "message": "Post with id: {} does not exist".format(kwargs["pk"])
                        },
                    status=status.HTTP_404_NOT_FOUND
                    )

    def put(self, request, *args, **kwargs):
        try:
            post = self.queryset.get(pk=kwargs["pk"])
            serializer = PostSerializerSchema(instance=post, data=request.data, context={"request": request})

            if serializer.is_valid(raise_exception=True):

                serializer.save()
                return Response(serializer.data)
            else:
                return Response(data=serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response(
                    data={
                        "message": "Post with id: {} does not exist".format(kwargs["pk"])
                        },
                    status=status.HTTP_404_NOT_FOUND
                    )

    def delete(self, request, *args, **kwargs):
        try:
            post = self.queryset.get(pk=kwargs["pk"])
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response(
                    data={
                        "message": "Post with id: {} does not exist".format(kwargs["pk"])
                        },
                    status=status.HTTP_404_NOT_FOUND
                    )
