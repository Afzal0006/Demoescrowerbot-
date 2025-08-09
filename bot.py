import os
import re
import random
from pymongo import MongoClient
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8414351117:AAEDEkc1VblJ8NU8Umle1gby1KyY94Gd1x4"
LOG_CHANNEL_ID = -1002330347621
OWNER_ID = 6998916494

# MongoDB connection
MONGO_URI = "mongodb+srv://afzal99550:afzal99550@cluster0.aqmbh9q.mongodb.net/escrow_bot?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["escrow_bot"]
data_col = db["data"]

# Load data
def load_data():
    doc = data_col.find_one({"_id": "config"})
    if not doc:
        default_data = {
            "_id": "config",
            "groups": {},
            "global": {"total_deals": 0, "total_volume": 0, "total_fee": 0.0, "escrowers": {}},
            "admins": []
        }
        data_col.insert_one(default_data)
        return default_data
    return doc

# Save data
def save_data():
    data_col.update_one({"_id": "config"}, {"$set": data}, upsert=True)

data = load_data()

# Functions remain same — start, add_admin, remove_admin, add_deal, complete_deal, stats, gstats

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
