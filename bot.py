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

# ✅ TOKEN from Render
TOKEN = os.getenv("BOT_TOKEN")

FILE_NAME = "user_data.txt"

# ✅ STATES
NAME, AGE, GENDER, MARRIED = range(4)

# ✅ START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your Name:")
    return NAME

# ✅ NAME
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your Age:")
    return AGE

# ✅ AGE
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    keyboard = [["Male", "Female"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Select Gender:", reply_markup=reply_markup)
    return GENDER

# ✅ GENDER
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text

    keyboard = [["Yes", "No"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Are you married?", reply_markup=reply_markup)
    return MARRIED

# ✅ SAVE DATA
async def get_married(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["married"] = update.message.text

    data = context.user_data

    with open(FILE_NAME, "a") as f:
        f.write(
            f"Name: {data['name']}, Age: {data['age']}, Gender: {data['gender']}, Married: {data['married']}\n"
        )

    await update.message.reply_text("✅ Data saved!")
    return ConversationHandler.END

# ✅ CANCEL
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ✅ SHOW DATA
async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(FILE_NAME, "r") as f:
            data = f.read()

        if data.strip() == "":
            data = "No data found"

        await update.message.reply_text(data)

    except FileNotFoundError:
        await update.message.reply_text("No file found")

# ✅ MAIN BOT LOGIC (NO UPDATER ERROR ✅)
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
    app.add_handler(CommandHandler("show", show_data))

    print("✅ Bot started...")

    # ✅ Proper start (FIXED)
    await app.initialize()
    await app.start()
    await app.bot.initialize()
    await app.run_polling()

# ✅ FLASK SERVER (FOR RENDER)
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Bot is running"

# ✅ THREAD FIX
def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

# ✅ START BOTH
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    flask_app.run(host="0.0.0.0", port=10000)
