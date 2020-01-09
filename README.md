# Issues Creator Bot

Issues Creator Bot is a Telegram bot made for creating issues at Gitlab and create Cards at Trello.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
See deployment for notes on how to deploy the project on a live system.

### Pre requisites

First clone the repository.
Then, create a Telegram Bot and get the token as explained
[here](https://core.telegram.org/bots#3-how-do-i-create-a-bot).
Save the token at the `TELEGRAM_BOT_TOKEN` in the `.env` file.

Create a Gitlab Private Token as explained
[here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#creating-a-personal-access-token).
Save the token at the `GITLAB_PRIVATE_TOKEN` in the `.env` file.

Create a Trello Token and API Key as explained
[here](https://developers.trello.com/docs/api-introduction#section-a-name-auth-authentication-and-authorization-a).
Save the token at the `TRELLO_TOKEN` and the `TRELLO_KEY` in the `.env` file.

Now you should be able to make requests to the Trello API as described
[here](https://developers.trello.com/docs/api-introduction#section-a-name-auth-your-first-api-call-a).
Get the `id` from the list where you want to create the new card and fill it at the `TRELLO_LIST_ID` in the `.env`file.

### Installation

I recommend you create a virtual environment with
```
virtualenv venv -p=python3
```
Now, you can install the prerequisites using pip
```
pip install -r requirements.txt
```
Now that you're ready to go. Just run the code
```
python src/issuesbot/main.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
