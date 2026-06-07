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

TOKEN = os.getenv("TOKEN")
FILE_NAME = "user_data.txt"

# ✅ States
NAME, AGE, GENDER, MARRIED = range(4)

# ✅ Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your Name:")
    return NAME

# ✅ Name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your Age:")
    return AGE

# ✅ Age
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    keyboard = [["Male", "Female"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Select Gender:", reply_markup=reply_markup)
    return GENDER

# ✅ Gender
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text

    keyboard = [["Yes", "No"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Are you married?", reply_markup=reply_markup)
    return MARRIED

# ✅ Married + Save
async def get_married(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["married"] = update.message.text

    data = context.user_data

    with open(FILE_NAME, "a") as f:
        f.write(
            f"Name: {data['name']}, Age: {data['age']}, Gender: {data['gender']}, Married: {data['married']}\n"
        )

    await update.message.reply_text("✅ Data saved successfully!")
    return ConversationHandler.END

# ✅ Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ✅ Telegram bot runner
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            MARRIED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_married)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("✅ Bot started...")
    await app.run_polling()

# ✅ Flask Web Server (for Render)
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Bot is running"

def start_bot():
    asyncio.run(run_bot())

# ✅ Run both
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    flask_app.run(host="0.0.0.0", port=10000)
