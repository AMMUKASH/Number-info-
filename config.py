import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Credentials (Set these in Render Environment Variables for security)
API_ID = int(os.getenv("API_ID", "38138069"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Bot & Owner Details
BOT_USERNAME = os.getenv("BOT_USERNAME", "@Nmbr_Info_bot")
OWNER_ID = int(os.getenv("OWNER_ID", "8724182918"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@CoderNova")

# Log Group & Media
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1003947649552"))
START_IMG = os.getenv("START_IMG", "https://files.catbox.moe/wcebdq.jpg")

# Links
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/NovaBot_Support")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/+KstoIqu4bgRlZGYx")

# Render Server Port
PORT = int(os.getenv("PORT", "10000"))
