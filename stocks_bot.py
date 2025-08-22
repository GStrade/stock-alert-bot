import os
import requests
import yfinance as yf
from telegram import Bot
from datetime import datetime

# קריאת משתנים סודיים מ-GitHub Secrets
TOKEN = os.getenv("TOKEN_STOCKS")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

# רשימת מניות לדוגמה (ניתן להרחיב)
CANDIDATES = ["PGEN", "PLTR", "SOFI", "BBBYQ", "NIO", "AMC"]

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5d")
    if data.empty:
        return None

    last = data.iloc[-1]
    prev = data.iloc[-2] if len(data) > 1 else last

    price = round(last["Close"], 2)
    change = round(((last["Close"] - prev["Close"]) / prev["Close"]) * 100, 2)

    info = stock.info
    sector = info.get("sector", "N/A")
    name = info.get("shortName", ticker)

    return {
        "ticker": ticker,
        "name": name,
        "price": price,
        "change": change,
        "sector": sector
    }

def filter_stocks():
    results = []
    for ticker in CANDIDATES:
        data = get_stock_data(ticker)
        if not data:
            continue
        # קריטריונים: מחיר בין 1 ל-20 דולר, שינוי יומי מעל 5%
        if 1 <= data["price"] <= 20 and abs(data["change"]) >= 5:
            results.append(data)
    return results[:5]  # עד 5 מניות

def format_message(stocks):
    if not stocks:
        return "לא נמצאו מניות מתאימות להיום."

    msg = "📊 *רשימת מניות חמות להיום:*\n\n"
    for s in stocks:
        direction = "🟢 לונג" if s["change"] > 0 else "🔴 שורט"
        msg += (
            f"*{s['ticker']}* ({s['name']})\n"
            f"מחיר: ${s['price']} | שינוי: {s['change']}%\n"
            f"סקטור: {s['sector']}\n"
            f"כיוון: {direction}\n"
            f"---\n"
        )
    return msg

def main():
    stocks = filter_stocks()
    text = format_message(stocks)
    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

if __name__ == "__main__":
    main()
