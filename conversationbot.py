#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging, sqlite3

from telegram import __version__ as TG_VER
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# using separate configuration and parser
from configparser import ConfigParser

# configparser
cfg = ConfigParser()
cfg.read('env.cfg')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Create database
db = sqlite3.connect('database.db')
# db.execute("DROP TABLE IF EXISTS users")
def savedb():
    print("Users Table:")
    [print(i) for i in db.execute("SELECT * FROM users")]
    print("HRV Table:")
    [print(i) for i in db.execute("SELECT * FROM hrv")]
    db.commit()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """List the possible commands for the bot."""

    await update.message.reply_text(
        "Hi! These are your availiable commands:\n"
        "/conv to have a casual conversation with me.\n"
        "/input to store your HRV data."
    )



########## Conversation ##########

GENDER, PHOTO, LOCATION, BIO = range(4)

db.execute("CREATE TABLE IF NOT EXISTS users(\
	id INTEGER NOT NULL PRIMARY KEY,\
	name TEXT, gender TEXT, photo TEXT,\
    location TEXT, bio TEXT)")


async def conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    reply_keyboard = [["Boy", "Girl", "Other"]]
    db.execute("INSERT INTO users (name) VALUES (?)", [user.first_name])
    savedb()

    await update.message.reply_text(
        "Hi! I am Myron's Bot ;) I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )

    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    db.execute("UPDATE users SET gender=? WHERE name=?", [update.message.text, user.first_name])
    savedb()

    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    filename = 'users/'+ user.first_name + user.last_name + ".jpg"
    await photo_file.download(filename)
    logger.info("Photo of %s: %s", user.first_name, filename)

    db.execute("UPDATE users SET photo=? WHERE name=?", [filename, user.first_name])
    savedb()

    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    
    db.execute("UPDATE users SET location=? WHERE name=?", [user_location, user.first_name])
    savedb()

    await update.message.reply_text(
        "Maybe I can visit you sometime! At last, tell me something about yourself."
    )

    return BIO


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid! At last, tell me something about yourself."
    )

    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    db.execute("UPDATE users SET bio=? WHERE name=?", [update.message.text, user.first_name])
    savedb()

    await update.message.reply_text("Thank you! I hope we can talk again some day.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    db.close()

    return ConversationHandler.END


########## HRV APP ##########

SUMMARY, GRAPHS, DETAILS = range(3)

db.execute("CREATE TABLE IF NOT EXISTS hrv(\
	id INTEGER NOT NULL PRIMARY KEY, name TEXT,\
    summary TEXT, graphs TEXT, details TEXT)")
def savedb():
    [print(i) for i in db.execute("SELECT * FROM hrv")]
    db.commit()


async def hrv_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the process of inputing hrv diagrams."""
    user = update.message.from_user
    logger.info("The user %s started hrv saving process", user.first_name)
    db.execute("INSERT INTO hrv (name) VALUES (?)", [user.first_name])
    savedb()

    await update.message.reply_text(
        "Hello there! I am the hrv bot.. \n"
        "Now you can send me your HRV data and I'll store them in my database for you :)"
        #"Or send /skip if you don't want to."
    )

    return SUMMARY


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    filename = 'hrv/'+ user.first_name + user.last_name + "-summary" +".jpg"
    await photo_file.download(filename)
    logger.info("Photo of %s: %s", user.first_name, filename)

    db.execute("UPDATE hrv SET summary=? WHERE name=?", [filename, user.first_name])
    savedb()

    await update.message.reply_text(
        "Great! Your data has been saved in the DataBase! \n"
        "Now you can send me  the HRV's graphs or input /skip to skip."
    )

    return GRAPHS


async def graphs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    filename = 'hrv/'+ user.first_name + user.last_name + "-graphs" +".jpg"
    await photo_file.download(filename)
    logger.info("Photo of %s: %s", user.first_name, filename)

    db.execute("UPDATE hrv SET graphs=? WHERE name=?", [filename, user.first_name])
    savedb()

    await update.message.reply_text(
        "Great! Your graphs has been saved in the DataBase! \n"
        "Now you can send me  the HRV's details or input /skip to skip."
    )

    return DETAILS


async def details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    filename = 'hrv/'+ user.first_name + user.last_name + "-details" +".jpg"
    await photo_file.download(filename)
    logger.info("Photo of %s: %s", user.first_name, filename)

    db.execute("UPDATE hrv SET details=? WHERE name=?", [filename, user.first_name])
    savedb()

    await update.message.reply_text(
        "Great! Your hrv details has been saved in the DataBase! \n"
        "Now all you HRV photos have been succesfully saved! :)"
    )

    return ConversationHandler.END


async def skip_hrv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the rest of hrv after summary."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return ConversationHandler.END



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(cfg['TELEGRAM']['token']).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("conv", conv)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    hrv_handler = ConversationHandler(
        entry_points=[CommandHandler("input", hrv_input)],
        states={
            SUMMARY: [MessageHandler(filters.PHOTO, summary)],
            GRAPHS: [MessageHandler(filters.PHOTO, graphs), CommandHandler("skip", skip_hrv)],
            DETAILS: [MessageHandler(filters.PHOTO, details), CommandHandler("skip", skip_hrv)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(hrv_handler)

    # Run the bot until the user presses Ctrl+C
    application.run_polling()



if __name__ == "__main__":
    main()