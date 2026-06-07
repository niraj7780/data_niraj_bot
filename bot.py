import os
import asyncio
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
FILE_NAME = "user_data.txt"

NAME, AGE, GENDER, MARRIED = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your Name:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your Age:")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    keyboard = [["Male", "Female"]]
    await update.message.reply_text(
        "Select Gender:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text

    keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        "Are you married?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return MARRIED

async def get_married(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["married"] = update.message.text

    data = context.user_data

    with open(FILE_NAME, "a") as f:
        f.write(f"{data['name']}, {data['age']}, {data['gender']}, {data['married']}\n")

    await update.message.reply_text("✅ Data saved!")
    return ConversationHandler.END

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(FILE_NAME, "r") as f:
            await update.message.reply_text(f.read() or "No data")
    except:
        await update.message.reply_text("No file found")

# ✅ Telegram bot runs in MAIN thread ✅
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            MARRIED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_married)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("show", show_data))

    print("✅ Bot started")
    await app.run_polling()

# ✅ Flask runs in background thread ✅
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot running ✅"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    # Flask in thread
    threading.Thread(target=run_flask).start()

    # Bot in main thread ✅
    asyncio.run(run_bot())
