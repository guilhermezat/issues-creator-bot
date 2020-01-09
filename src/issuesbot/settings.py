import os
from dotenv import load_dotenv

load_dotenv()

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID")

GITLAB_PRIVATE_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")
PROJECT_FILTER = os.getenv("PROJECT_FILTER")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

SECRET_KEY = os.getenv("SECRET_KEY")

