from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from posts.serializers import PostSerializerSchema
from tests.base import BaseViewTest

class PostModelTest(APITestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title="Ugandan anthem",
            body="George William Kakoma",
            author=self.user
        )

    def test_post(self):
        """"
        This test ensures that the song created in the setup
        exists
        """
        self.assertEqual(self.post.title, "Ugandan anthem")
        self.assertEqual(self.post.body, "George William Kakoma")
        self.assertEqual(str(self.post), "Ugandan anthem - George William Kakoma")


class GetAllPostsTest(BaseViewTest):

    def test_get_all_posts(self):
        """
        This test ensures that all songs added in the setUp method
        exist when we make a GET request to the songs/ endpoint
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.client.get(
            reverse("post-list-create")
        )
        # fetch the data from db
        expected = Post.objects.all()
        serialized = PostSerializerSchema(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetASingleSongsTest(BaseViewTest):

    def test_get_a_song(self):
        """
        This test ensures that a single song of a given id is
        returned
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.fetch_a_post(self.valid_post_id)
        # fetch the data from db
        expected = Post.objects.get(pk=self.valid_post_id)
        serialized = PostSerializerSchema(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a song that does not exist
        response = self.fetch_a_post(self.invalid_song_id)
        self.assertEqual(
            response.data["message"],
            "Song with id: 100 does not exist"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddSongsTest(BaseViewTest):

    def test_create_a_post(self):
        """
        This test ensures that a single song can be added
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.make_a_request(
            kind="post",
            data=self.valid_data
        )
        self.assertEqual(response.data, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.make_a_request(
            kind="post",
            data=self.invalid_data
        )
        self.assertEqual(
            response.data["message"],
            "Both title and body are required to add a song"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateSongsTest(BaseViewTest):

    def test_update_a_song(self):
        """
        This test ensures that a single song can be updated. In this
        test we update the second song in the db with valid data and
        the third song with invalid data and make assertions
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.make_a_request(
            kind="put",
            id=2,
            data=self.valid_data
        )
        self.assertEqual(response.data, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with invalid data
        response = self.make_a_request(
            kind="put",
            id=3,
            data=self.invalid_data
        )
        self.assertEqual(
            response.data["message"],
            "Both title and body are required to add a song"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteSongsTest(BaseViewTest):

    def test_delete_a_song(self):
        """
        This test ensures that when a song of given id can be deleted
        """
        self.login_client('test_user', 'testing')
        # hit the API endpoint
        response = self.delete_a_post(1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # test with invalid data
        response = self.delete_a_post(100)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)