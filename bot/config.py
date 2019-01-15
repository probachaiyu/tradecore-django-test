import configparser

import os


from bot.bot_client import BotClient

config = configparser.ConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')

def createConfig():
    """
    Create a config file
    """
    config.add_section("DEFAULT")
    config.set("DEFAULT", "number_of_users", 3)
    config.set("DEFAULT", "max_posts_per_user", 5)
    config.set("DEFAULT", "max_likes_per_user", 3)

    with open(CONFIG_PATH, "w") as config_file:
        config.write(config_file)


def get_config():
    if not os.path.exists(CONFIG_PATH):
        createConfig()

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    return BotClient(config.get('DEFAULT', 'number_of_users'), config.get('DEFAULT', 'max_posts_per_user'),
                     config.get('DEFAULT', 'max_likes_per_user'))
