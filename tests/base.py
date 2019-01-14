import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from posts.models import Post

User = get_user_model()

class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_post(title="", body="", user=None):
        """
        Create a song in the db
        :param title:
        :param artist:
        :return:
        """
        if title != "" and body != "" and user!=None:
            Post.objects.create(title=title, body=body, author=user)

    def make_a_request(self, kind="post", **kwargs):
        """
        Make a post request to create a post
        :param kind: HTTP VERB
        :return:
        """
        if kind == "post":
            return self.client.post(
                reverse(
                    "post-list-create",
                ),
                data=json.dumps(kwargs["data"]),
                content_type='application/json'
            )
        elif kind == "put":
            return self.client.put(
                reverse(
                    "post-detail",
                    kwargs={
                        "pk": kwargs["id"]
                    }
                ),
                data=json.dumps(kwargs["data"]),
                content_type='application/json'
            )
        else:
            return None

    def fetch_a_post(self, pk=0):
        return self.client.get(
            reverse(
                "post-detail",
                kwargs={
                    "pk": pk
                }
            )
        )

    def delete_a_post(self, pk=0):
        return self.client.delete(
            reverse(
                "post-detail",
                kwargs={
                    "pk": pk
                }
            )
        )

    def login_a_user(self, username="", password=""):
        url = reverse(
            "auth-login",
        )
        return self.client.post(
            url,
            data=json.dumps({
                "username": username,
                "password": password
            }),
            content_type="application/json"
        )

    def login_client(self, username="", password=""):
        # get a token from DRF
        response = self.client.post(
            reverse("create-token"),
            data=json.dumps(
                {
                    'username': username,
                    'password': password
                }
            ),
            content_type='application/json'
        )
        self.token = response.data['token']
        # set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.token
        )
        self.client.login(username=username, password=password)
        return self.token

    def register_a_user(self, username="", password="", email=""):
        return self.client.post(
            reverse(
                "auth-register",
            ),
            data=json.dumps(
                {
                    "username": username,
                    "password": password,
                    "email": email
                }
            ),
            content_type='application/json'
        )

    def setUp(self):
        # create a admin user
        self.user = User.objects.create_superuser(
            username="test_user",
            email="test@mail.com",
            password="testing",
            first_name="test",
            last_name="user",
        )
        # add test data
        self.create_post("like glue", "sean paul", self.user)
        self.create_post("simple song", "konshens", self.user)
        self.create_post("love is wicked", "brick and lace", self.user)
        self.create_post("jam rock", "damien marley", self.user)
        self.valid_data = {
            "title": "test title",
            "body": "test body",
            "author": self.user
        }
        self.invalid_data = {
            "title": "",
            "body": ""
        }
        self.valid_post_id = 1
        self.invalid_song_id = 100
