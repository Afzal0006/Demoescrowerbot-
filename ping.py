from pyrogram import Client, filters
import time
from datetime import datetime

@Client.on_message(filters.command("ping"))
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
