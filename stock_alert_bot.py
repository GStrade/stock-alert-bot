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
    # 🔔 הודעת בדיקה בתחילת ההרצה
    bot.send_message(chat_id=CHAT_ID, text="🔔 הבוט הופעל בהצלחה, מתחיל סריקה...")

    tickers = ['NIO', 'BITF', 'COMP', 'AMC', 'ADT', 'SMWB']
    results = []

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

            if len(reasons) >= 2 and price:
                direction = "לונג" if change > 0 else "שורט"
                potential = round(abs(change), 2)
                entry = round(price * 0.98, 2)
                stop = round(price * 0.90, 2)
                tp1 = round(price * 1.15, 2)
                tp2 = round(price * 1.30, 2)

                results.append({
                    "symbol": t,
                    "name": info.get('shortName', t),
                    "sector": sector,
                    "price": price,
                    "reasons": reasons,
                    "direction": direction,
                    "potential": potential,
                    "entry": entry,
                    "stop": stop,
                    "tp1": tp1,
                    "tp2": tp2
                })
        except Exception as e:
            print(f"שגיאה עם {t}: {e}")

    results = results[:5]

    if not results:
        bot.send_message(chat_id=CHAT_ID, text="לא נמצאו מניות מתאימות היום.")
        return

    # הודעה מסודרת
    message = "📊 *עדכון מניות יומי*\n\n"
    for r in results:
        message += f"**{r['name']} ({r['symbol']})** — {r['sector']}\n"
        message += f"מחיר נוכחי: ${r['price']:.2f}\n"
        message += f"כיוון: {r['direction']}\n"
        message += f"סיבה: {', '.join(r['reasons'])}\n"
        message += f"כניסה: ${r['entry']} (הדרגתי)\n"
        message += f"סטופ: ${r['stop']}\n"
        message += f"יעדים: TP1 ${r['tp1']} (+15%) | TP2 ${r['tp2']} (+30%)\n"
        message += f"הערכת סיכוי: ~{r['potential']}%\n\n"

    message += "*הערה*: לא ייעוץ השקעות. לשיקולך בלבד."

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

    # גרפים לכל מניה
    for r in results:
        chart_path = generate_chart(r['symbol'])
        bot.send_photo(chat_id=CHAT_ID, photo=open(chart_path, 'rb'), caption=f"{r['symbol']} – גרף יומי")

    # ✅ הודעת סיום בדיקה
    bot.send_message(chat_id=CHAT_ID, text="✅ הבוט סיים סריקה")

send_stocks()
