import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("TOKEN")  # use env variable
FILE_NAME = "user_data.txt"

# States
NAME, AGE, GENDER, MARRIED = range(4)

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your First Name:")
    return NAME

# ✅ Save name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Enter your Age:")
    return AGE

# ✅ Save age
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text

    keyboard = [["Male", "Female"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Select your Gender:", reply_markup=reply_markup
    )
    return GENDER

# ✅ Save gender
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text

    keyboard = [["Yes", "No"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Are you married?", reply_markup=reply_markup
    )
    return MARRIED

# ✅ Save married + write file
async def get_married(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["married"] = update.message.text

    data = context.user_data

    # Save to file
    with open(FILE_NAME, "a") as f:
        f.write(
            f"Name: {data['name']}, Age: {data['age']}, Gender: {data['gender']}, Married: {data['married']}\n"
        )

    await update.message.reply_text("✅ Data saved successfully!")

    return ConversationHandler.END

# ✅ Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ✅ Main function
def main():
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

    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
