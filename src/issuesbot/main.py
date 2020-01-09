# -*- coding: utf-8 -*-
import json
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from settings import TELEGRAM_BOT_TOKEN, SECRET_KEY, GITLAB_PRIVATE_TOKEN, PROJECT_FILTER
from issue import Issue

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Stages
PROJECT, TITLE, DESCRIPTION, CONFIRM, CREATE = range(5)


def show_help(update, context):
    update.message.reply_text(
        "Sou um bot para criar issues.\n"
        "Para iniciar é só digitar /start\n"
        "Quando quiser parar ou cancelar o processo é só digitar /cancel"
    )
    # Tell ConversationHandler that we're in state `PROJECT` now
    return ConversationHandler.END


def start(update, context):
    """Send message on `/start`.
    Fetch the projects that the user is member at the gitlab
    """
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    logger.info(f"The user data context: {context.user_data}")
    context.user_data.clear()

    r = requests.get('https://git.pti.org.br/api/v4/projects',
                     headers={
                         'Content-type': 'application/json',
                         'Private-token': GITLAB_PRIVATE_TOKEN
                     },
                     params={
                         'simple': True,
                         'search': PROJECT_FILTER
                     })
    projects = r.json()
    logging.info(f'Received projects: {projects}')

    # Remove the unnecessary data from the project object
    # We only need the project name to display for the user
    # and the project id so we can create the issue at Gitlab
    projects = [
        {
            'name': project['name'],
            'id': project['id']
        } for project in projects
    ]
    logging.info(f'Projects sent for the user: {projects}')

    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard_projects = [
        InlineKeyboardButton(project['name'], callback_data=json.dumps(project)) for project in projects
    ]

    # Create a function called "chunks" with two arguments, l and n:
    def chunks(l, n):
        # For item i in a range that is a length of l,
        for i in range(0, len(l), n):
            # Create an index range for l of n items:
            yield l[i:i + n]

    keyboard = list(chunks(keyboard_projects, 1))

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Sou um bot para criar issues.\n"
                              "Para iniciar é só digitar /start\n"
                              "Quando quiser parar ou cancelar o processo é só digitar /cancel\n\n"
                              "Escolha um projeto para criar a issue",
                              reply_markup=reply_markup
                              )

    # Tell ConversationHandler that we're in state `PROJECT` now
    return PROJECT


def project_choice(update, context):
    query = update.callback_query
    bot = context.bot
    logging.info(f'Query: {query} - Bot: {bot}')
    logger.info(f"The user data context: {context.user_data}")

    # Store the project choice at the user data context
    context.user_data['project'] = json.loads(query.data)

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"Projeto {context.user_data['project']['name']} escolhido.\n"
             f"Digite o título para a issue.",
        reply_markup=None
    )
    # Tell ConversationHandler that we're in state `TITLE` now
    return TITLE


def issue_title(update, context):
    user = update.message.from_user
    logger.info("Titulo fornecido por %s: %s", user.first_name, update.message.text)
    logger.info(f"The user data context: {context.user_data}")

    # Store the issue title at the user data context
    context.user_data['title'] = update.message.text

    update.message.reply_text(f'O título da issue é: {context.user_data["title"]}.\n'
                              f'Agora digite uma descrição.',
                              reply_markup=None
                              )
    # Tell ConversationHandler that we're in state `DESCRIPTION` now
    return DESCRIPTION


def issue_description(update, context):
    user = update.message.from_user
    logger.info(f"Descrição fornecida por {user.first_name}: {update.message.text}")
    logger.info(f"The user data context: {context.user_data}")

    # Store the issue description at the user data context
    context.user_data['description'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Ok", callback_data='1'),
         InlineKeyboardButton("Foda-se", callback_data='0')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"Vou criar a issue com o título \"{context.user_data['title']}\" "
        f"no projeto \"{context.user_data['project']['name']}\" "
        f"com a descrição \"{context.user_data['description']}\".\n"
        f"Tudo certo?",
        reply_markup=reply_markup
    )
    # Tell ConversationHandler that we're in state `CONFIRM` now
    return CONFIRM


def confirm_issue(update, context):
    query = update.callback_query
    bot = context.bot
    logging.info(f'Query: {query} - Bot: {bot}')
    logger.info(f"The user data context: {context.user_data}")

    if json.loads(query.data):
        message = f'Blz, agora confirme com a palavra secreta'
        state = CREATE
    else:
        message = f'De boa. Fica pra próxima ;)'
        state = ConversationHandler.END

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=message,
        reply_markup=None
    )
    # Tell ConversationHandler that we're in state `CREATE` now
    return state


def confirm_issue_creation(update, context):
    user = update.message.from_user
    logger.info(f"Palavra secreta digitada por {user.first_name}: {update.message.text}")
    logger.info(f"The user data context: {context.user_data}")
    issue = Issue(
        context.user_data['project'],
        context.user_data['title'],
        context.user_data['description']
    )

    if update.message.text == SECRET_KEY:
        message = f'Acertou mizerávi\n\n'
        if issue.create_issue():
            message += f'Issue Criada :)\n'
        else:
            message += f'Desculpa pelo vacilo!\n' \
                       f'Tive um problema para criar a issue\n'

        if issue.create_card():
            message += f'Card Criado :)'
        else:
            message += f'Desculpa pelo vacilo!\n' \
                       f'Tive um problema para criar o card'
    else:
        message = f'Errrrooouu!'

    update.message.reply_text(
        message,
        reply_markup=None
    )
    # Tell ConversationHandler that the conversation has ended
    return ConversationHandler.END


def cancel(update, context):
    """"Cancel the conversation"""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    logger.info(f"The user data context: {context.user_data}")

    update.message.reply_text('Criação da issue cancelada.\n'
                              'Tchau! :(',
                              reply_markup=None)
    # Tell ConversationHandler that the conversation has ended
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    logger.info(f"The user data context: {context.user_data}")


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Setup conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler(Filters.text,
                                     show_help)],
        states={
            PROJECT: [CallbackQueryHandler(project_choice)],
            TITLE: [MessageHandler(Filters.text,
                                   issue_title)],
            DESCRIPTION: [MessageHandler(Filters.text,
                                         issue_description)],
            CONFIRM: [CallbackQueryHandler(confirm_issue)],
            CREATE: [MessageHandler(Filters.text,
                                    confirm_issue_creation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add ConversationHandler to dispatcher that will be used for handling
    # updates
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
