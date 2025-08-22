import os
import telebot

TOKEN = os.getenv("TOKEN_STOCKS")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

bot.send_message(CHAT_ID, "✅ בדיקת חיבור - בוט המניות מחובר בהצלחה!")
print("נשלחה הודעת בדיקה לטלגרם")
