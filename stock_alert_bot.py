
import yfinance as yf
import matplotlib.pyplot as plt
from telegram import Bot
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_sector(info):
    return info.get("sector", "לא ידוע")

def get_direction(info):
    if info.get("targetMeanPrice", 0) > info.get("previousClose", 0):
        return "לונג"
    else:
        return "שורט"

def send_stocks():
    sectors_allowed = ["Technology", "Financial Services", "Energy", "Communication Services"]

    tickers = ['NIO', 'BITF', 'COMP', 'AMC', 'ADT', 'SMWB']
    bot = Bot(token=TOKEN)
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="5d")
            price = hist['Close'][-1]
            if not (1 <= price <= 20):
                continue

            info = stock.info
            name = info.get("shortName", t)
            summary = info.get("longBusinessSummary", "")[:150]
            sector = get_sector(info)
            if sector not in sectors_allowed: continue
            direction = get_direction(info)
            target = info.get("targetMeanPrice", 0)
            previous = info.get("previousClose", 0)
            profit = ((target - previous) / previous * 100) if previous else 0

            # יצירת גרף ושמירה
            hist['Close'].plot(title=f"{t} - גרף יומי")
            plt.ylabel("מחיר ($)")
            plt.tight_layout()
            image_path = f"{t}.png"
            plt.savefig(image_path)
            plt.close()

            # ניסוח ההודעה
            msg = f"*{name}* ({t})\n"
            msg += f"מחיר נוכחי: {price:.2f}$\n"
            msg += f"תחום: {sector}\n"
            msg += f"סיבה: {summary}...\n"
            msg += f"כיוון: {direction}\n"
            msg += f"פוטנציאל רווח: {profit:.1f}%\n"

            bot.send_photo(chat_id=CHAT_ID, photo=open(image_path, "rb"), caption=msg, parse_mode="Markdown")
            os.remove(image_path)
        except Exception as e:
            print(f"שגיאה במניה {t}: {e}")

send_stocks()
