import re
import random
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


BOT_TOKEN = "8414351117:AAEDEkc1VblJ8NU8Umle1gby1KyY94Gd1x4"
DATA_FILE = "data.json"
LOG_CHANNEL_ID = -1002330347621
OWNER_ID = 6998916494


def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "groups": {},
            "global": {"total_deals": 0, "total_volume": 0, "total_fee": 0.0, "escrowers": {}},
            "admins": []
        }


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


data = load_data()


# ✅ OWNER + custom admins only
async def is_admin(update: Update) -> bool:
    user_id = update.effective_user.id
    return user_id == OWNER_ID or user_id in data.get("admins", [])


def init_group(chat_id: str):
    if chat_id not in data["groups"]:
        data["groups"][chat_id] = {
            "deals": {},
            "total_deals": 0,
            "total_volume": 0,
            "total_fee": 0.0,
            "escrowers": {}
        }


def update_escrower_stats(group_id: str, escrower: str, amount: float, fee: float):
    g = data["groups"][group_id]
    g["total_deals"] += 1
    g["total_volume"] += amount
    g["total_fee"] += fee
    g["escrowers"][escrower] = g["escrowers"].get(escrower, 0) + amount


    data["global"]["total_deals"] += 1
    data["global"]["total_volume"] += amount
    data["global"]["total_fee"] += fee
    data["global"]["escrowers"][escrower] = data["global"]["escrowers"].get(escrower, 0) + amount


    save_data()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "✨ <b>Welcome to Demo Escrower Bot!</b> ✨\n\n"
        "🤖 <b>I am here to manage escrow deals securely.</b>\n"
        "💡 Use me to hold payments safely until trades are complete.\n\n"
        "📋 <b>My Commands:</b>\n"
        "• <b>/add</b> – Add a new deal\n"
        "• <b>/complete</b> – Complete a deal\n"
        "• <b>/stats</b> – Group stats\n"
        "• <b>/gstats</b> – Global stats (Admin only)\n"
        "• <b>/addadmin user_id</b> – Owner only\n"
        "• <b>/removeadmin user_id</b> – Owner only\n\n"
        "🛡️ <i>Secure your trades with confidence!</i>"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only bot owner can use this command!")
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /addadmin <user_id>")
        return
    user_id = int(context.args[0])
    if user_id in data["admins"]:
        await update.message.reply_text("⚠️ This user is already an admin.")
    else:
        data["admins"].append(user_id)
        save_data()
        await update.message.reply_text(f"✅ User {user_id} added as admin.")


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only bot owner can use this command!")
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /removeadmin <user_id>")
        return
    user_id = int(context.args[0])
    if user_id in data["admins"]:
        data["admins"].remove(user_id)
        save_data()
        await update.message.reply_text(f"✅ User {user_id} removed from admin list.")
    else:
        await update.message.reply_text("⚠️ This user is not an admin.")


async def add_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    try:
        await update.message.delete()
    except:
        pass
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to the DEAL INFO form message!")
        return
    original_text = update.message.reply_to_message.text
    chat_id = str(update.effective_chat.id)
    reply_id = str(update.message.reply_to_message.message_id)
    init_group(chat_id)
    buyer_match = re.search(r"BUYER\s*:\s*(@\w+)", original_text, re.IGNORECASE)
    seller_match = re.search(r"SELLER\s*:\s*(@\w+)", original_text, re.IGNORECASE)
    amount_match = re.search(r"DEAL AMOUNT\s*:\s*₹?\s*([\d.]+)", original_text, re.IGNORECASE)
    buyer = buyer_match.group(1) if buyer_match else "Unknown"
    seller = seller_match.group(1) if seller_match else "Unknown"
    if not amount_match:
        await update.message.reply_text("❌ Amount not found in the form!")
        return
    amount = float(amount_match.group(1))
    group_data = data["groups"][chat_id]
    if reply_id not in group_data["deals"]:
        trade_id = f"TID{random.randint(100000, 999999)}"
        fee = 0.0
        release_amount = round(amount - fee, 2)
        group_data["deals"][reply_id] = {
            "trade_id": trade_id,
            "release_amount": release_amount,
            "completed": False
        }
    else:
        trade_id = group_data["deals"][reply_id]["trade_id"]
        release_amount = group_data["deals"][reply_id]["release_amount"]
        fee = round(amount - release_amount, 2)
    escrower = (
        f"@{update.effective_user.username}" 
        if update.effective_user.username 
        else update.effective_user.full_name
    )
    update_escrower_stats(chat_id, escrower, amount, fee)
    msg = (
        "✅ <b>Amount Received!</b>\n"
        "────────────────\n"
        f"👤 <b>Buyer</b>  : {buyer}\n"
        f"👤 <b>Seller</b> : {seller}\n"
        f"💰 <b>Amount</b> : ₹{amount}\n"
        f"💸 <b>Release</b>: ₹{release_amount}\n"
        f"⚖️ <b>Fee</b>    : ₹{fee}\n"
        f"🆔 <b>Trade ID</b>: #{trade_id}\n"
        "────────────────\n"
        f"🛡️ <b>Escrowed by</b> {escrower}"
    )
    await update.effective_chat.send_message(msg, reply_to_message_id=update.message.reply_to_message.message_id, parse_mode="HTML")
    save_data()


async def complete_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    try:
        await update.message.delete()
    except:
        pass
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to the DEAL INFO form message!")
        return
    chat_id = str(update.effective_chat.id)
    reply_id = str(update.message.reply_to_message.message_id)
    init_group(chat_id)
    group_data = data["groups"][chat_id]
    deal_info = group_data["deals"].get(reply_id)
    if not deal_info:
        await update.message.reply_text("❌ This deal was never added with /add!")
        return
    if deal_info["completed"]:
        await update.message.reply_text("❌ This deal is already completed!")
        return
    deal_info["completed"] = True
    save_data()
    original_text = update.message.reply_to_message.text
    buyer_match = re.search(r"BUYER\s*:\s*(@\w+)", original_text, re.IGNORECASE)
    seller_match = re.search(r"SELLER\s*:\s*(@\w+)", original_text, re.IGNORECASE)
    buyer = buyer_match.group(1) if buyer_match else "Unknown"
    seller = seller_match.group(1) if seller_match else "Unknown"
    trade_id = deal_info["trade_id"]
    release_amount = deal_info["release_amount"]
    escrower = (
        f"@{update.effective_user.username}" 
        if update.effective_user.username 
        else update.effective_user.full_name
    )
    msg = (
        "✅ <b>Deal Completed!</b>\n"
        "────────────────\n"
        f"👤 <b>Buyer</b>   : {buyer}\n"
        f"👤 <b>Seller</b>  : {seller}\n"
        f"💸 <b>Released</b>: ₹{release_amount}\n"
        f"🆔 <b>Trade ID</b>: #{trade_id}\n"
        "────────────────\n"
        f"🛡️ <b>Escrowed by</b> {escrower}"
    )
    await update.effective_chat.send_message(msg, reply_to_message_id=update.message.reply_to_message.message_id, parse_mode="HTML")
    log_msg = (
        "📜 <b>Deal Completed (Log)</b>\n"
        "────────────────\n"
        f"👤 <b>Buyer</b>   : {buyer}\n"
        f"👤 <b>Seller</b>  : {seller}\n"
        f"💸 <b>Released</b>: ₹{release_amount}\n"
        f"🆔 <b>Trade ID</b>: #{trade_id}\n"
        f"🛡️ <b>Escrowed by</b> {escrower}\n\n"
        f"📌 <b>Group</b>: {update.effective_chat.title} ({update.effective_chat.id})"
    )
    await context.bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="HTML")


async def group_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    init_group(chat_id)
    g = data["groups"][chat_id]
    escrowers_text = "\n".join([f"{name} = ₹{amt}" for name, amt in g["escrowers"].items()]) or "No deals yet"
    msg = (
        f"📊 Escrow Bot Stats\n\n"
        f"{escrowers_text}\n\n"
        f"🔹 Total Deals: {g['total_deals']}\n"
        f"💰 Total Volume: ₹{g['total_volume']}\n"
        f"💸 Total Fee Collected: ₹{g['total_fee']}\n"
    )
    await update.message.reply_text(msg)


async def global_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    g = data["global"]
    escrowers_text = "\n".join([f"{name} = ₹{amt}" for name, amt in g["escrowers"].items()]) or "No deals yet"
    msg = (
        f"🌍 Global Escrow Stats\n\n"
        f"{escrowers_text}\n\n"
        f"🔹 Total Deals: {g['total_deals']}\n"
        f"💰 Total Volume: ₹{g['total_volume']}\n"
        f"💸 Total Fee Collected: ₹{g['total_fee']}\n"
    )
    await update.message.reply_text(msg)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_deal))
    app.add_handler(CommandHandler("complete", complete_deal))
    app.add_handler(CommandHandler("stats", group_stats))
    app.add_handler(CommandHandler("gstats", global_stats))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    print("Bot started... ✅")
    app.run_polling()


if __name__ == "__main__":

    main()
