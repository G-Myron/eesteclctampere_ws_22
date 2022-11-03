import logging

from telegram import __version__ as TG_VER

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
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# using separate configuration and parser
from configparser import ConfigParser
# import initdb and handler to it
import initdatabase
import db_handler
# get access to data plotter
import matplotlib.pyplot as plt
import numpy

# configparser
cfg = ConfigParser()
cfg.read('env.cfg')

# get token from config
TOKEN = cfg['TELEGRAM']['token']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# declaring constants
STOREDATA, PLOTDATA = range(2)

# calling method initdb creates 
initdatabase.initdb()

# when /start is issued
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays starting message and lists commands."""
    await update.message.reply_text(
        "Welcome. Use the commands below to test available features.\n"
        "/help lists these commands.\n"
        "/new let's you input new data value.\n"
        "/plot function initiates plotting of chosen data.\n"
        "/cancel cancels current action.\n"
        # TODO: add the commands you need.  
    )

# when /help is issued
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text(
        "/new let's you input new data value.\n"
        "/plot function initiates plotting of chosen data.\n"
        "/cancel cancels current action.\n"
        # TODO: add commands you need here too
    )

# when /cancel is issued
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Action cancelled."
    )
    return ConversationHandler.END

# this /new command initiates this conversation and returns constant STOREDATA
async def newdata(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks new data point value from user."""
    # TODO: expand this so that we can store different kind of data.
    await update.message.reply_text(
        "Waiting for new value: "
    )
    return STOREDATA
    
# called when STOREDATA state is reached 
async def store_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stores the aquired data by calling add_data method from db_handler."""

    user = update.message.from_user
    new_data = update.message.text

    # we are calling add_data method from database handler
    # # it takes the new_data as parameter 
    db_handler.add_data(new_data)

    # Logging new_data and username
    logger.info(
        "Stored new value %s from user %s", new_data , user.first_name
        )

    await update.message.reply_text(
        "Stored new value: "
    )
    await update.message.reply_text(update.message.text)

    return ConversationHandler.END

# called when /plot command is given
async def plotter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks user what data they want to plot."""
    await update.message.reply_text(
        "What data do you want to plot?\n"
        "Options: data"
        #TODO: expand if you want to plot from several different datasources
    )
    return PLOTDATA

# called when PLOTDATA state is reached in plotter_handler conversation
async def plot_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gets new data value from user."""
    user = update.message.from_user
    chosen_data = update.message.text
    logger.info(
        "Plotting data: %s from user: %s", chosen_data , user.first_name
        )

    await update.message.reply_text(
        "Plotting.. : "
    )

    # getdatapoint method is called from db_handler
    data = db_handler.getdatapoint()
    # received data is given as a parameter to plot method from data plotter
    plot(data)
    
    # replies to user with plotted graph
    await update.message.reply_photo(photo=open('data_plot.png','rb'))
    await update.message.reply_text(update.message.text)
    return ConversationHandler.END

def plot(data):
    hrv_datetime = {}
    hrv_timestamps = []
    hrv_datapoints = []
    for row in data:
        print(row)
        date = row[0].split(" ")[0]
        time = row[0].split(" ")[1]
        hrv_datetime['year'] = int(date.split("-")[0])
        hrv_datetime['month'] = int(date.split("-")[1])
        hrv_datetime['day'] = int(date.split("-")[2])
        hrv_datetime['hour'] = int(time.split(":")[0])
        hrv_datetime['minute'] = int(time.split(":")[1])
        print(hrv_datetime['month'])
        print(hrv_datetime['day'])
        print(hrv_datetime['hour'])
        hrv_timestamps.append(hrv_datetime['day'])
        hrv_datapoints.append(int(row[1]))

    plt.plot(hrv_datapoints)
    plt.xlabel('Time')
    plt.ylabel('Value (unit)')
    plt.savefig('data_plot.png')

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    storedata_handler = ConversationHandler(
        entry_points=[CommandHandler("new", newdata)],
        states={
            # This is a message handler, takes user input from message
            STOREDATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    plotter_handler = ConversationHandler(
        entry_points=[CommandHandler("plot", plotter)],
        states={
            PLOTDATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, plot_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(storedata_handler)
    application.add_handler(plotter_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()