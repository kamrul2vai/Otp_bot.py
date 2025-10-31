from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = "8204988226:AAF4tIxMQTaGI3R0BkKDDVFhBOxqCZ0BpnE"

numbers = []
used_numbers = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Next Number 🔁"], ["Add Number ➕", "Reset ♻️"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "📞 Hey KAMZ! Your Number Bot Is Ready.\n\n"
        "You can upload a .txt file or use /add to add numbers manually.",
        reply_markup=markup
    )

async def add_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global numbers
    text = update.message.text.replace("/add", "").strip()
    new_numbers = [line.strip() for line in text.splitlines() if line.strip()]

    count_before = len(numbers)
    numbers.extend(new_numbers)
    count_after = len(numbers)

    await update.message.reply_text(
        f"✅ Added {count_after - count_before} numbers!\nTotal Numbers: {len(numbers)}"
    )

async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global numbers, used_numbers

    if not numbers:
        await update.message.reply_text("⚠️ No numbers available. Please upload or add some.")
        return

    unused_numbers = [n for n in numbers if n not in used_numbers]

    if not unused_numbers:
        await update.message.reply_text("✅ All numbers have been used!")
        return

    number = unused_numbers[0]
    used_numbers.append(number)

    if not number.startswith("+"):
        number = "+" + number

    remain_left = len(numbers) - len(used_numbers)
    reply_keyboard = [["Next Number 🔁"], ["Add Number ➕", "Reset ♻️"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    # Mono style (backticks)
    message = (
        f"📞 Hey KAMZ! Your Number Is -\n\n"
        f"`{number}`\n\n"
        f"Remain Left: {remain_left}"
    )

    await update.message.reply_text(message, reply_markup=markup, parse_mode="Markdown")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global numbers, used_numbers
    numbers.clear()
    used_numbers.clear()

    reply_keyboard = [["Next Number 🔁"], ["Add Number ➕", "Reset ♻️"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "♻️ All numbers deleted!\nUpload a new .txt file or use /add to start again.",
        reply_markup=markup
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global numbers
    file = await update.message.document.get_file()
    file_path = "numbers.txt"
    await file.download_to_drive(file_path)

    with open(file_path, "r") as f:
        new_numbers = [line.strip() for line in f if line.strip()]

    numbers.extend(new_numbers)
    os.remove(file_path)

    reply_keyboard = [["Next Number 🔁"], ["Add Number ➕", "Reset ♻️"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"📄 {len(new_numbers)} numbers uploaded successfully!\nTotal Numbers: {len(numbers)}",
        reply_markup=markup
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Next Number 🔁":
        await get_number(update, context)
    elif text == "Add Number ➕":
        await update.message.reply_text("✍️ Send numbers like:\n\n/add\n12345\n67890\n...")
    elif text == "Reset ♻️":
        await reset(update, context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_numbers))
    app.add_handler(CommandHandler("get", get_number))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.Document.FileExtension("txt"), handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))

    print("🤖 KAMZ Number Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
