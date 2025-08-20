
import yfinance as yf
from telegram import Bot
import matplotlib.pyplot as plt
import os

# --- פרטי הבוט ---
TOKEN = '8087060265:AAGSzuUJuvqv0jd7XhtNiKcXbnbBiI3pEds'
CHAT_ID = 1715673393

# --- רשימת מניות לדוגמה ---
TICKERS = ['NIO', 'BITF', 'COMP', 'AMC', 'ADT', 'SMWB', 'MARA', 'RIOT', 'SOUN', 'NVOS', 'GME', 'BBBY', 'TSLA', 'NVDA']

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="7d")
        if hist.empty or len(hist) < 2:
            return None

        info = stock.info
        name = info.get('shortName', ticker)
        sector = info.get('sector', 'לא ידוע')
        volume = info.get('volume', 0)
        avg_volume = info.get('averageVolume', 1)
        volume_ratio = volume / avg_volume if avg_volume else 0
        price_today = hist['Close'][-1]
        price_yesterday = hist['Close'][-2]
        change_pct = ((price_today - price_yesterday) / price_yesterday) * 100

        score = 0
        reasons = []

        # שינוי יומי
        if abs(change_pct) >= 5:
            score += 1
            reasons.append(f"שינוי יומי חריג: {change_pct:+.1f}%")

        # ווליום חריג
        if volume_ratio >= 2:
            score += 1
            reasons.append(f"ווליום חריג: פי {volume_ratio:.1f}")

        # חדשות (קישור בלבד)
        score += 1
        reasons.append("🔔 חדשות חמות")

        # פריצה טכנית (פשוטה)
        if change_pct > 5 and volume_ratio > 3:
            score += 1
            reasons.append("🚀 פריצה טכנית")

        if score >= 3:
            direction = "לונג" if change_pct > 0 else "שורט"
            potential = abs(change_pct) * 1.5
            chance = "גבוה" if score == 4 else "בינוני"

            # יצירת גרף
            plt.figure(figsize=(5,3))
            hist['Close'].plot(title=f"{ticker} - גרף יומי")
            plt.tight_layout()
            filename = f"{ticker}.png"
            plt.savefig(filename)
            plt.close()

            message = (
                f"*{name}* ({ticker})\n"
                f"מגזר: {sector}\n"
                f"📌 כיוון העסקה: *{direction}*\n"
                f"🎯 סיבת כניסה: {', '.join(reasons)}\n"
                f"📈 פוטנציאל רווח: ~{potential:.1f}%\n"
                f"📊 סיכויי הצלחה: {chance}\n"
                f"[לגרף ב-Yahoo](https://finance.yahoo.com/quote/{ticker})"
            )
            return message, filename
    except:
        return None

    return None

def send_to_telegram(text, image_path):
    bot = Bot(token=TOKEN)
    bot.send_photo(chat_id=CHAT_ID, photo=open(image_path, 'rb'), caption=text, parse_mode='Markdown')
    os.remove(image_path)

# --- הרצה ---
results = []
for t in TICKERS:
    result = analyze_stock(t)
    if result:
        results.append(result)
    if len(results) == 5:
        break

if results:
    for text, img in results:
        send_to_telegram(text, img)
else:
    Bot(token=TOKEN).send_message(chat_id=CHAT_ID, text="⏳ לא נמצאו מניות מתאימות היום.")
