import os
import yfinance as yf
import matplotlib.pyplot as plt
from telegram import Bot

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

def get_sector(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("sector", "לא ידוע")
    except:
        return "שגיאה"

def generate_chart(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="7d")
    plt.figure()
    hist['Close'].plot(title=f"{ticker} - גרף יומי")
    filepath = f"{ticker}.png"
    plt.savefig(filepath)
    plt.close()
    return filepath

def send_stocks():
    tickers = ['NIO', 'BITF', 'COMP', 'AMC', 'ADT', 'SMWB']
    msgs = []

    for t in tickers:
        try:
            stock = yf.Ticker(t)
            info = stock.info
            price = stock.history(period="1d")['Close'][0]
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', 1)
            change = info.get('regularMarketChangePercent', 0)
            sector = get_sector(t)

            reasons = []
            if change > 5:
                reasons.append("📈 שינוי יומי חד")
            if volume > 2 * avg_volume:
                reasons.append("🔥 ווליום חריג")
            if info.get('newsHeadline', ''):
                reasons.append("📰 חדשות חמות")

            if len(reasons) >= 2:
                summary = info.get('longBusinessSummary', '')[:100]
                direction = "לונג" if change > 0 else "שורט"
                potential = round(abs(change), 2)
                chart_path = generate_chart(t)
                caption = f"*{info.get('shortName', t)}* ({t})\nתחום: {sector}\nסיבה: {', '.join(reasons)}\nכיוון: {direction}\nאחוז רווח פוטנציאלי: {potential}%\n{summary}..."
                bot.send_photo(chat_id=CHAT_ID, photo=open(chart_path, 'rb'), caption=caption, parse_mode='Markdown')
        except Exception as e:
            print(f"שגיאה עם {t}: {e}")

send_stocks()
