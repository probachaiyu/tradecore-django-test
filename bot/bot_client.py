import logging
import os
import random

import sys
from itertools import count

import django
from django.db.models import Subquery, Q

parent_dir = os.path.abspath(os.path.join(os.getcwd(), ""))
sys.path.append(parent_dir)
django.setup()
import names
from django.db import models, connection
from bot.services import RequestClient, RandomCreator
from posts.models import Post
from users.models import User


class BotClient():
    options = {
        'DOMAIN': 'http://127.0.0.1:8000',
        'LOGIN': '/users/auth/login/',
        'REGISTER': '/users/auth/register/',
        'CREATE_POST': '/posts/',
        }

    def __init__(self, number_of_users, max_posts_per_user, max_likes_per_user):
        self.number_of_users = number_of_users
        self.max_posts_per_user = max_posts_per_user
        self.max_likes_per_user = max_likes_per_user

    def register_user(self):
        username = RandomCreator.get_name()
        password = RandomCreator.create_password()
        data = {"username": username, "password": password, "email": RandomCreator.get_email()}
        res = RequestClient.make_request(self.get_url(self.options["REGISTER"]), data)
        return username, password, res["id"]

    def create_post(self, count, token, user_id):
        data = {"title": "Post %s" % count,
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                        "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                        "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                        "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat "
                        "cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                "author": user_id}
        return RequestClient.authenticated_request(self.get_url(self.options["CREATE_POST"]), data=data, token=token)

    def login_user(self, username, password):
        data = {"username": username, "password": password}
        result = RequestClient.make_request(self.get_url(self.options["LOGIN"]), data)
        return result["token"]

    def get_url(self, part_url):
        return '{}{}'.format(self.options["DOMAIN"], part_url)

    def start_activity(self):
        passwords = {}
        for i in range(int(self.number_of_users)):
            username, password, user_id = self.register_user()
            logging.warning("User %s registered" % username)

            token = self.login_user(username, password)
            logging.warning("User %s logged in" % username)
            posts_number = random.randint(1, int(self.max_posts_per_user))
            for j in range(posts_number):
                self.create_post(j, token, user_id)
            logging.warning("User {} created {} number of posts".format(username, posts_number))
            passwords[username] = password
        return passwords

    def get_posts(self, current_author_id):
        authors = Post.objects.values('likes').annotate(
                t_likes=models.Count("likes")
                ).filter(t_likes=0).values('author_id').distinct()
        posts = Post.objects.filter(author__in=authors)
        return posts

    def perform_likes(self, passwords):
        for user in User.objects.annotate(posts=models.Count('post')):
            logging.warning("User %s posts is starting likes" % user.username)

            token = self.login_user(user.username, passwords.get(user.username))

            posts = self.get_posts(user.id)

            logging.warning("There are %s posts with 0 vote user can like" % len(posts))

            if not posts:
                logging.warning("Liking is finished")
                break
            for k in range(random.randint(1, int(self.max_likes_per_user))):
                current_post = random.choice(posts)
                res = RequestClient.authenticated_request(
                    url=self.get_url('{}{}{}'.format(self.options["CREATE_POST"], current_post.id, '/vote')),
                    token=token)
                logging.warning("User liked post %s", current_post.id)
                posts.exclude(id=current_post.id)

    def run(self):
        passwords = self.start_activity()
        self.perform_likes(passwords)


if __name__ == "__main__":
    path = "settings.ini"
    from bot.config import get_config

    bot = get_config()
    bot.run()
