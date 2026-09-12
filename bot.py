import os
import requests
import asyncio
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

QUOTEX_EMAIL = os.getenv("QUOTEX_EMAIL")
QUOTEX_PASSWORD = os.getenv("QUOTEX_PASSWORD")

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Telegram Error: {e}")

async def run_trade_cycle():
    if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
        print("Error: Quotex credentials missing!")
        send_telegram_message("❌ *Error:* Quotex credentials missing in GitHub Secrets!")
        return

    # ১ মিনিট বা ট্রেড শুরু হওয়ার একটু আগে সিগন্যাল পাঠানোর জন্য সময় ক্যালকুলেশন
    now = datetime.now()
    target_time = now + timedelta(minutes=1)
    formatted_time = target_time.strftime("%H:%M")
    
    asset = "EUR/USD (OTC)"
    
    # সিগন্যাল মেসেজ (১ মিনিট আগে বা সময়মতো এলার্টসহ)
    signal_message = (
        f"🚨 *Upcoming Quotex Signal Alert* 🚨\n\n"
        f"📊 Pair: **{asset}**\n"
        f"⏳ Timeframe: **1 Minute**\n"
        f"🎯 Action: 🟢 **CALL (BUY)**\n"
        f"⏰ Target Time: **{formatted_time}**\n\n"
        f"⚠️ *Get ready for the trade!*"
    )
    send_telegram_message(signal_message)
    print(f"Signal sent for target time: {formatted_time}")

if __name__ == "__main__":
    asyncio.run(run_trade_cycle())
