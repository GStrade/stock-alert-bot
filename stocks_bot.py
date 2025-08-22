import os
from telegram import Bot

TOKEN = os.getenv("TOKEN_STOCKS")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

def main():
    bot.send_message(chat_id=CHAT_ID, text="✅ הודעת בדיקה – בוט המניות מחובר ועובד!")

if __name__ == "__main__":
    main()
