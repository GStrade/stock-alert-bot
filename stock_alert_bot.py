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
    hist = stock.history(period="6mo")
    plt.figure(figsize=(8,4))
    hist['Close'].plot(title=f"{ticker} - גרף יומי")
    filepath = f"{ticker}.png"
    plt.savefig(filepath)
    plt.close()
    return filepath

def send_stocks():
    tickers = ['NIO', 'BITF', 'COMP', 'AMC', 'ADT', 'SMWB']
    results = []  # רשימה לאגירת המניות שנבחרו

    for t in tickers:
        try:
            stock = yf.Ticker(t)
            info = stock.info
            hist = stock.history(period="1d")
            price = hist['Close'][0] if not hist.empty else None
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', 1)
            change = info.get('regularMarketChangePercent', 0)
            sector = get_sector(t)

            reasons = []
            if change and change > 5:
                reasons.append("📈 שינוי יומי חד")
            if volume and avg_volume and volume > 2 * avg_volume:
                reasons.append("🔥 ווליום חריג")
            if info.get('newsHeadline', ''):
                reasons.append("📰 חדשות חמות")

            # שולחים רק אם יש לפחות 2 סיבות
            if len(reasons) >= 2 and price:
                summary = info.get('longBusinessSummary', '')[:100]
                direction = "לונג" if change > 0 else "שורט"
                potential = round(abs(change), 2)
                results.append({
                    "symbol": t,
                    "name": info.get('shortName', t),
                    "sector": sector,
                    "price": price,
                    "reasons": reasons,
                    "direction": direction,
                    "potential": potential,
                    "summary": summary
                })
        except Exception as e:
            print(f"שגיאה עם {t}: {e}")

    # מגבילים ל-5 מניות
    results = results[:5]

    if not results:
        bot.send_message(chat_id=CHAT_ID, text="לא נמצאו מניות מתאימות היום.")
        return

    # בונים הודעה מסודרת
    message = "📊 *עדכון מניות יומי*\n\n"
    for r in results:
        message += f"*{r['name']}* ({r['symbol']})\n"
        message += f"תחום: {r['sector']}\n"
        message += f"מחיר: ${r['price']:.2f}\n"
        message += f"סיבה: {', '.join(r['reasons'])}\n"
        message += f"כיוון: {r['direction']}\n"
        message += f"אחוז רווח פוטנציאלי: {r['potential']}%\n"
        message += f"{r['summary']}...\n\n"

    # שליחת ההודעה
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

    # שליחת גרפים לכל מניה
    for r in results:
        chart_path = generate_chart(r['symbol'])
        caption = f"{r['symbol']} – גרף יומי"
        bot.send_photo(chat_id=CHAT_ID, photo=open(chart_path, 'rb'), caption=caption)

send_stocks()
