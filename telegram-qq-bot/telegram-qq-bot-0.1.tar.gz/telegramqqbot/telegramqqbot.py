from pyqqclient.SmartqqClient import SmartqqClient
from pyqqclient.Logger import logger
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import RegexHandler
from telegram.ext import ConversationHandler
import threading


BOT_LOGIN, IDLE, LOGGED_IN = range(3)


def error(bot, update, received_error):
    logger.warning('Update "%s" caused error "%s"' % (update, received_error))


def start_handler(bot, update, user_data):
    update.message.reply_text("Hello there, if you're my master, type the password below:")
    user_data["subscribed_contact"] = set()
    user_data["subscribed_group"] = set()
    user_data["logged_in"] = False
    return BOT_LOGIN


def stop_handler(bot, update, user_data):
    update.message.reply_text("bye.")
    user_data.clear()
    return ConversationHandler.END


def login_handler(bot, update, user_data):
    def login_done():
        user_data["logged_in"] = True
        update.message.reply_text("You've logged in successfully")
    client = SmartqqClient(
        barcode_handler=lambda barcode: update.message.reply_photo(
            barcode, caption="Please scan the barcode to login."
        ),
        # db_identify_string=update.message.chat_id,
        login_done_handler=login_done
    )
    user_data["client"] = client
    client_thread = threading.Thread(target=client.run)
    user_data["client_thread"] = client_thread
    client_thread.start()
    return LOGGED_IN


def bot_login_handler(bot,update):
    if update.message.text == "mypasswd":
        update.message.reply_text("Welcome, my master")
        return IDLE
    else:
        update.message.reply_text("You're not my master!\nRetry:")
        return BOT_LOGIN


def main():
    updater = Updater("TOKEN")
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error)

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_handler, pass_user_data=True)
        ],
        states={
            BOT_LOGIN: [MessageHandler(Filters.text, bot_login_handler)],
            IDLE: [CommandHandler("login", login_handler, pass_user_data=True)],
            LOGGED_IN: []
        },
        fallbacks=[
            CommandHandler("stop", stop_handler, pass_user_data=True)
        ]
    )

    dispatcher.add_handler(conversation_handler)
    updater.start_polling()

if __name__ == '__main__':
    main()
