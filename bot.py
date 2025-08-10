import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ====== BOT CREDENTIALS ======
BOT_TOKEN = "8414351117:AAEDEkc1VblJ8NU8Umle1gby1KyY94Gd1x4"

# ====== /start COMMAND ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text
# ====== /ping COMMAND ======
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await update.message.reply_text(f"Pong! 🏓\nLatency: {latency} ms\nTime: {now}")

# ====== MAIN FUNCTION ======
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()

