import logging
from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from pymongo import MongoClient

# ===== CONFIG =====
BOT_TOKEN = "7648809089:AAHWY1RieRjc0loC5mf0omLgE7WDuPt3xVQ"
MONGO_URI = "mongodb+srv://afzal99550:afzal99550@cluster0.aqmbh9q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
OWNER_ID = 5086305853

CHANNEL_URL = "https://t.me/sixclubgiftcodeofficial"

# Images
START_PHOTO = "https://i.ibb.co/CssQ3kRK/x.jpg"
PHOTO_28 = "https://i.ibb.co/KxzwKRN7/x.jpg"
PHOTO_GIFT = "https://i.ibb.co/nN9tDvVG/x.jpg"
PHOTO_PREMIUM = "https://i.ibb.co/rGSkr410/x.jpg"
PHOTO_WINGO = "https://i.ibb.co/YBnBwnWn/x.jpg"
PHOTO_SPIN = "https://i.ibb.co/0k8ZzGK/x.jpg"
PHOTO_CONTACT = "https://i.ibb.co/1tCpgQ2p/x.jpg"
PHOTO_AGENT = "https://i.ibb.co/HppHKhNf/x.jpg"

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)

# ===== DB =====
client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_col = db["users"]
stats_col = db["stats"]

stats_col.update_one(
    {"_id": "start"},
    {"$setOnInsert": {"count": 0}},
    upsert=True
)

# ===== KEYBOARD =====
keyboard = [
    ["💰 Register To Get 28₹"],
    ["⏰ 24/7 Giftcode Exclusive Channel 🤑", "🎰 6 Club PREMIUM-Prediction 🏆"],
    ["🔴🟢 Wingo Forecasting Team 📈", "🎯 Spin & Get FREE ₹300"],
    ["👉Contact Us For Agent Work😎", "😇 24/7 CUSTOMER SERVICE ✅"],
]
reply_kb = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== START MESSAGE =====
START_TEXT = (
    "🔑 VIP GIFT CODES की Exclusive List! 🤫\n"
    "रोज़ 500₹ से 1000₹ तक पक्का Profit! 🤑\n"
    "50₹+50₹+50₹ से शुरुआत करें! ✅\n"
    "यह Limited Offer जल्द खत्म हो जाएगा!\n\n"
    "📌इस Link Se Account Banao 👇\n"
    "https://www.6clubj.com/#/register?invitationCode=41671111853\n\n"
    "👉तुरंत Register करो नीचे 5 Giftcodes है Register करके Account बना लो और सभी Giftcodes Claim कर लो ! 🤞\n\n"
    "《50+50+50+50+50 FREE GIFT》\n\n"
    "F0B2B47680CDD027C97F84307F7ACE37\n\n"
    "46596F08546B3A36B24144AF233F0B46\n\n"
    "C37AF014DD62A98C6ACB788CB62772A3\n\n"
    "F3A84464AFB83D7F91C495751C5A83A7\n\n"
    "9F7102042CB4F5B4010BC0A54747D643\n\n"
    "👇👇 Daily Free New GIFTCODE के लिए चैनल Join करें 👇👇"
)

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Save user if new
    if not users_col.find_one({"_id": user.id}):
        users_col.insert_one({
            "_id": user.id,
            "name": user.full_name,
            "username": user.username
        })

    # Increase start count
    stats_col.update_one(
        {"_id": "start"},
        {"$inc": {"count": 1}},
        upsert=True
    )

    # Inline buttons (2 buttons)
    inline_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "JOIN 𝘿𝘼𝙄𝙇𝙔 𝙁𝙍𝙀𝙀 𝙂𝙄𝙁𝙏𝘾𝙊𝘿𝙀 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 ✅",
                url=CHANNEL_URL
            )
        ],
        [
            InlineKeyboardButton(
                "𝗖𝗹𝗮𝗶𝗺 𝟯𝟬𝟬 𝗯𝗼𝗻𝘂𝘀",
                url="https://www.6clubj.com/#/register?invitationCode=41671111853"  # 👈 yahan apna URL daal do
            )
        ]
    ])

    # Send start photo with inline buttons
    await update.message.reply_photo(
        photo=START_PHOTO,
        caption=START_TEXT,
        reply_markup=inline_kb
    )

    # Show reply keyboard menu
    await update.message.reply_text(
        "🔝 Main Menu",
        reply_markup=reply_kb
    )

# ===== /stats =====
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = users_col.count_documents({})

    text = (
        "📊 Bot Stats\n\n"
        f"👤 Total Users: {total_users}"
    )
    await update.message.reply_text(text)

# ===== BUTTON HANDLER =====
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 Register To Get 28₹":
        msg = (
            "⭐Register To Get ₹28\n"
            "https://www.6clubj.com/#/register?invitationCode=41671111853"
        )
        await update.message.reply_photo(photo=PHOTO_28, caption=msg)

    elif text == "⏰ 24/7 Giftcode Exclusive Channel 🤑":
        msg = (
            "💸 आज का गिफ्टकोड आ गया! 💸 | कलर\n"
            "प्रेडिक्शन गेम में फ्री एंट्री! 🎟️| हर दिन नया कोड! ✅ तुरंत टेलीग्राम से जुड़ें! 🏆🏆\n\n"
            "💯Register Link ✅✅\n"
            "https://www.6clubj.com/#/register?invitationCode=41671111853\n\n"
            "🚀FREE GIFTCODE CHANNEL LINK🚀\n"
            "https://t.me/sixclubgiftcodeofficial\n"
            "https://t.me/sixclubgiftcodeofficial\n\n"
            "👆👆👆👆👆👆👆👆👆👆👆👆"
        )
        await update.message.reply_photo(photo=PHOTO_GIFT, caption=msg)

    elif text == "🎰 6 Club PREMIUM-Prediction 🏆":
        msg = (
            "💡 सिग्नल की ताकत! 💪 हमारे नए चैनल पर BIG-SMALL और Number की सबसे Accurate Predictions मिल रही हैं! 🤩 एक Click आपका Future बदल देगा!  तुरंत Check करें और Join करें! \n\n"
            "OFFICIAL REGISTER LINK ✅✅\n"
            "https://www.6clubj.com/#/register?invitationCode=41671111853\n\n"
            "J O I N F A S T 👇🥳\n"
            "https://t.me/sixclubgiftcodeofficial\n"
            "https://t.me/sixclubgiftcodeofficial"
        )
        await update.message.reply_photo(photo=PHOTO_PREMIUM, caption=msg)

    elif text == "🔴🟢 Wingo Forecasting Team 📈":
        msg = (
            "⚠️​ कम Risk, बड़ा Profit! ⚠️ BIG-SMALL की 3-4 लेवल Accurate Wining Prediction के लिए सही जगह! 💰 Guarantee के साथ Join करें! 😍😍😍😍\n"
            "OFFICIAL REGISTER LINK ✅✅\n"
            "https://www.6clubj.com/#/register?invitationCode=41671111853\n\n"
            "J O I N F A S T 👇🥳\n"
            "https://t.me/sixclubgiftcodeofficial\n"
            "https://t.me/sixclubgiftcodeofficial"
        )
        await update.message.reply_photo(photo=PHOTO_WINGO, caption=msg)

    elif text == "🎯 Spin & Get FREE ₹300":
        msg = (
            "🌈 Spin the Wheel & Win BIG! 💰\n\n"
            "📌App Link👇👇\n"
            "https://www.6clubj.com/#/register?invitationCode=41671111853\n\n"
            "🌟Guaranteed rewards from ₹300 to ₹2000 – Try your luck NOW!✔️"
        )
        await update.message.reply_photo(photo=PHOTO_SPIN, caption=msg)

    elif text == "👉Contact Us For Agent Work😎":
        msg = (
            "Contact the tutor Anushka👇\n"
            "http://t.me/anushka7773\n"
            "http://t.me/anushka7773"
        )
        await update.message.reply_photo(photo=PHOTO_AGENT, caption=msg)

    elif text == "😇 24/7 CUSTOMER SERVICE ✅":
        msg = (
            "👋 Hello my name is Anushka, if you have any kind of problem please contact me\n"
            "👉 @anushka7773 👈\n"
            "👉 @anushka7773 👈\n\n"
            "दोस्तो आपको किसी भी तरह की समस्या है तो कृपया बेझिझक मुझसे संपर्क करें ✅\n"
            "👉 @anushka7773 👈\n"
            "👉 @anushka7773 👈"
        )
        await update.message.reply_photo(photo=PHOTO_CONTACT, caption=msg)
# ===== /broadcast (OWNER ONLY) =====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ Only owner can use this command!")

    users = list(users_col.find())
    total = len(users)
    ok, fail = 0, 0
    target = update.message.reply_to_message

    status_msg = await update.message.reply_text("📢 Broadcast started...")

    # 👉 Text broadcast
    if not target:
        if not context.args:
            return await status_msg.edit_text(
                "Use:\n/broadcast <message>\nOr reply to any message with /broadcast"
            )

        msg = " ".join(context.args)

        for u in users:
            try:
                await context.bot.send_message(chat_id=u["_id"], text=msg)
                ok += 1
            except:
                fail += 1

        return await status_msg.edit_text(
            f"📢 Broadcast Completed\n\nSent = {ok}/{total}"
        )

    # 👉 Media/Text by reply
    for u in users:
        try:
            chat_id = u["_id"]

            if target.photo:
                await context.bot.send_photo(chat_id, target.photo[-1].file_id, caption=target.caption or "")
            elif target.video:
                await context.bot.send_video(chat_id, target.video.file_id, caption=target.caption or "")
            elif target.document:
                await context.bot.send_document(chat_id, target.document.file_id, caption=target.caption or "")
            elif target.animation:
                await context.bot.send_animation(chat_id, target.animation.file_id, caption=target.caption or "")
            elif target.text:
                await context.bot.send_message(chat_id, target.text)

            ok += 1
        except:
            fail += 1

    await status_msg.edit_text(
        f"📢 Broadcast Completed\n\nSent = {ok}/{total}"
    )
# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
