from pyrogram import Client, filters
import time
from datetime import datetime

# ==== CONFIG ====
API_ID = 20917743
API_HASH = "0e8bcef16b3bae4f852bf42775f04ace"
BOT_TOKEN = "8414351117:AAEDEkc1VblJ8NU8Umle1gby1KyY94Gd1x4"

# ==== BOT INSTANCE ====
app = Client(
    "my_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ==== PING COMMAND ====
@app.on_message(filters.command("ping"))
async def ping(_, message):
    start = time.time()
    m = await message.reply_text("Pinging...")
    end = time.time()

    ping_time = round((end - start) * 1000)
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    await m.edit_text(
        f"🏓 **Pong!**\n"
        f"⏱ **Latency:** `{ping_time} ms`\n"
        f"🕒 **Time:** `{current_time}`"
    )

# ==== START BOT ====
if __name__ == "__main__":
    print("✅ Bot started successfully!")
    app.run()
