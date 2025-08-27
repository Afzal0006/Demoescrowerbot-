import re, random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pymongo import MongoClient

# ==== CONFIG ====
BOT_TOKEN = "8466069044:AAFaAtC5qDnZI8p8QkxsHOONKdjhJCKdRmk"
MONGO_URI = "mongodb+srv://GfNF2cIHLNozy5Q2:GfNF2cIHLNozy5Q2@cluster0.8wjyhsl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
LOG_CHANNEL_ID = -1002829010235
OWNER_IDS = [7363327309]

# ==== MONGO CONNECT ====
client = MongoClient(MONGO_URI)
db = client["escrow_bot"]
groups_col, global_col, admins_col = db["groups"], db["global"], db["admins"]

if not global_col.find_one({"_id": "stats"}):
    global_col.insert_one({"_id":"stats","total_deals":0,"total_volume":0,"total_fee":0.0,"escrowers":{}})

# ==== HELPERS ====
async def is_admin(update: Update):
    uid = update.effective_user.id
    return uid in OWNER_IDS or admins_col.find_one({"user_id": uid}) is not None

def init_group(chat_id):
    if not groups_col.find_one({"_id": chat_id}):
        groups_col.insert_one({"_id":chat_id,"deals":{},"total_deals":0,"total_volume":0,"total_fee":0.0,"escrowers":{}})

def update_stats(group_id, escrower, amount, fee):
    g = groups_col.find_one({"_id": group_id})
    g["total_deals"] += 1
    g["total_volume"] += amount
    g["total_fee"] += fee
    g["escrowers"][escrower] = g["escrowers"].get(escrower,0)+amount
    groups_col.update_one({"_id": group_id},{"$set":g})

    gd = global_col.find_one({"_id":"stats"})
    gd["total_deals"] += 1
    gd["total_volume"] += amount
    gd["total_fee"] += fee
    gd["escrowers"][escrower] = gd["escrowers"].get(escrower,0)+amount
    global_col.update_one({"_id":"stats"},{"$set":gd})

# ==== COMMANDS ====
async def start(update, context):
    await update.message.reply_text(
        "✨ <b>Welcome to Escrower Bot!</b> ✨\n\n"
        "• /add – Add a new deal\n"
        "• /complete – Complete a deal\n"
        "• /stats – Group stats\n"
        "• /gstats – Global stats (Admin only)\n"
        "• /mystats – Your stats (buyer/seller/escrower)\n"
        "• /addadmin user_id – Owner only\n"
        "• /removeadmin user_id – Owner only", parse_mode="HTML")

async def add_admin(update, context):
    if update.effective_user.id not in OWNER_IDS: return await update.message.reply_text("❌ Only owners!")
    if len(context.args)!=1 or not context.args[0].isdigit(): return await update.message.reply_text("Usage: /addadmin <user_id>")
    uid=int(context.args[0])
    if admins_col.find_one({"user_id":uid}): return await update.message.reply_text("⚠️ Already admin!")
    admins_col.insert_one({"user_id":uid})
    await update.message.reply_text(f"✅ Added admin: {uid}")

async def remove_admin(update, context):
    if update.effective_user.id not in OWNER_IDS: return await update.message.reply_text("❌ Only owners!")
    if len(context.args)!=1 or not context.args[0].isdigit(): return await update.message.reply_text("Usage: /removeadmin <user_id>")
    uid=int(context.args[0]); admins_col.delete_one({"user_id":uid})
    await update.message.reply_text(f"✅ Removed admin: {uid}")

async def add_deal(update, context):
    if not await is_admin(update): return
    try: await update.message.delete()
    except: pass
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to DEAL INFO!")

    text = update.message.reply_to_message.text
    chat_id=str(update.effective_chat.id)
    rid=str(update.message.reply_to_message.message_id)
    init_group(chat_id)

    buyer = re.search(r"BUYER\s*:\s*(@\w+)", text, re.I)
    seller = re.search(r"SELLER\s*:\s*(@\w+)", text, re.I)
    amount = re.search(r"DEAL AMOUNT\s*:\s*₹?\s*([\d.]+)", text, re.I)
    buyer=buyer.group(1) if buyer else "Unknown"; seller=seller.group(1) if seller else "Unknown"
    if not amount: return await update.message.reply_text("❌ Amount not found!")
    amount=float(amount.group(1))

    g = groups_col.find_one({"_id":chat_id})
    deals = g["deals"]
    escrower=f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.full_name

    if rid not in deals:
        tid=f"TID{random.randint(100000,999999)}"; fee=0.0
        release=round(amount-fee,2)
        deals[rid]={"trade_id":tid,"release_amount":release,"completed":False,"escrower":escrower,"buyer":buyer,"seller":seller}
    else: tid=deals[rid]["trade_id"]; release=deals[rid]["release_amount"]; fee=round(amount-release,2)

    g["deals"]=deals; groups_col.update_one({"_id":chat_id},{"$set":g})
    update_stats(chat_id, escrower, amount, fee)

    await update.effective_chat.send_message(
        f"✅ <b>Amount Received!</b>\n────────────────\n👤 Buyer : {buyer}\n👤 Seller : {seller}\n💰 Amount : ₹{amount}\n💸 Release: ₹{release}\n⚖️ Fee : ₹{fee}\n🆔 Trade ID: #{tid}\n────────────────\n🛡️ Escrowed by {escrower}",
        reply_to_message_id=update.message.reply_to_message.message_id, parse_mode="HTML")

async def complete_deal(update, context):
    if not await is_admin(update): return
    try: await update.message.delete()
    except: pass
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to DEAL INFO!")

    chat_id=str(update.effective_chat.id)
    rid=str(update.message.reply_to_message.message_id)
    g=groups_col.find_one({"_id":chat_id})
    deal=g["deals"].get(rid)
    if not deal: return await update.message.reply_text("❌ Deal not found!")
    if deal["completed"]: return await update.message.reply_text("⚠️ Already completed!")

    deal["completed"]=True; g["deals"][rid]=deal
    groups_col.update_one({"_id":chat_id},{"$set":g})

    escrower,buyer,seller,release,tid = deal["escrower"],deal.get("buyer","Unknown"),deal.get("seller","Unknown"),deal["release_amount"],deal["trade_id"]
    await update.effective_chat.send_message(
        f"✅ <b>Deal Completed!</b>\n────────────────\n👤 Buyer: {buyer}\n👤 Seller: {seller}\n💸 Released: ₹{release}\n🆔 Trade ID: #{tid}\n────────────────\n🛡️ Escrowed by {escrower}",
        reply_to_message_id=update.message.reply_to_message.message_id, parse_mode="HTML")
    await context.bot.send_message(LOG_CHANNEL_ID,
        f"📜 <b>Deal Completed (Log)</b>\n────────────────\n👤 Buyer: {buyer}\n👤 Seller: {seller}\n💸 Released: ₹{release}\n🆔 Trade ID: #{tid}\n🛡️ Escrowed by {escrower}\n📌 Group: {update.effective_chat.title} ({update.effective_chat.id})", parse_mode="HTML")

# ==== STATS COMMANDS ====
async def group_stats(update, context):
    chat_id=str(update.effective_chat.id); init_group(chat_id)
    g=groups_col.find_one({"_id":chat_id})
    text="\n".join([f"{n} = ₹{a}" for n,a in g["escrowers"].items()]) or "No deals yet"
    await update.message.reply_text(f"📊 Group Stats\n\n{text}\n\n🔹 Total Deals: {g['total_deals']}\n💰 Total Volume: ₹{g['total_volume']}\n💸 Total Fee: ₹{g['total_fee']}")

async def global_stats(update, context):
    if not await is_admin(update): return
    g=global_col.find_one({"_id":"stats"})
    text="\n".join([f"{n} = ₹{a}" for n,a in g["escrowers"].items()]) or "No deals yet"
    await update.message.reply_text(f"🌍 Global Stats\n\n{text}\n\n🔹 Total Deals: {g['total_deals']}\n💰 Total Volume: ₹{g['total_volume']}\n💸 Total Fee: ₹{g['total_fee']}")

async def my_stats(update, context):
    uid = update.effective_user.username or str(update.effective_user.id)
    total_deals = total_volume = total_fee = 0
    deals_list=[]
    # check all groups
    for g in groups_col.find():
        for deal in g["deals"].values():
            if uid in [deal.get("buyer"), deal.get("seller"), deal.get("escrower")]:
                total_deals +=1
                total_volume += deal["release_amount"]
                deals_list.append(f"🆔 {deal['trade_id']} | Buyer: {deal['buyer']} | Seller: {deal['seller']} | Release: ₹{deal['release_amount']}")
    msg = f"📊 <b>Your Stats</b>\n\nTotal Deals: {total_deals}\nTotal Volume: ₹{total_volume}\n\nDeals:\n" + ("\n".join(deals_list) if deals_list else "No deals yet")
    await update.message.reply_text(msg, parse_mode="HTML")

# ==== MAIN ====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_deal))
    app.add_handler(CommandHandler("complete", complete_deal))
    app.add_handler(CommandHandler("stats", group_stats))
    app.add_handler(CommandHandler("gstats", global_stats))
    app.add_handler(CommandHandler("mystats", my_stats))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    print("Bot is running... 💨")
    app.run_polling()

if __name__ == "__main__":
    main()




