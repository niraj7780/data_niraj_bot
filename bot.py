import os
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

# ---------- BOT LOGIC ----------

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
    data = context.user_data
    data["married"] = update.message.text

    with open(FILE_NAME, "a") as f:
        f.write(f"{data['name']}, {data['age']}, {data['gender']}, {data['married']}\n")

    await update.message.reply_text("✅ Data saved!")
    return ConversationHandler.END

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(FILE_NAME, "r") as f:
            text = f.read()

        if not text:
            text = "No data found"

        await update.message.reply_text(text)
    except:
        await update.message.reply_text("No file found")

# ---------- START BOT ----------

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            MARRIED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_married)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("show", show_data))

    print("✅ Bot started successfully")
    app.run_polling()   # ✅ NO asyncio.run()

# ---------- FLASK ----------

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Bot running"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# ---------- MAIN ----------

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()   # ✅ main thread → no error
