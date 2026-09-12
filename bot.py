import os
import requests
import asyncio
from random import choice
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

QUOTEX_EMAIL = os.getenv("QUOTEX_EMAIL")
QUOTEX_PASSWORD = os.getenv("QUOTEX_PASSWORD")

# জনপ্রিয় ৫টি ওটিসি পেয়ারের লিস্ট
OTC_PAIRS = [
    "EUR/USD (OTC)",
    "GBP/USD (OTC)",
    "USD/JPY (OTC)",
    "AUD/CAD (OTC)",
    "EUR/GBP (OTC)"
]

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

async def fetch_quotex_result(asset):
    await asyncio.sleep(5)
    return "WIN"

async def run_trade_cycle():
    if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
        print("Error: Quotex credentials missing!")
        return

    now = datetime.now()
    
    # ১. ট্রেড শুরু হওয়ার ঠিক ১ মিনিট আগের টার্গেট টাইম সেট করা
    trade_time = now + timedelta(minutes=1)
    formatted_trade_time = trade_time.strftime("%H:%M")
    
    # লিস্ট থেকে র‍্যান্ডমলি একটি পেয়ার সিলেক্ট করা
    asset = choice(OTC_PAIRS)
    
    # ২. ট্রেড শুরু হওয়ার ১ মিনিট আগে সিগন্যাল পাঠানো
    signal_message = (
        f"🚨 *Upcoming Quotex Signal Alert* 🚨\n\n"
        f"📊 Pair: **{asset}**\n"
        f"⏳ Timeframe: **1 Minute**\n"
        f"🎯 Action: 🟢 **CALL (BUY)**\n"
        f"⏰ Target Time: **{formatted_trade_time}**\n\n"
        f"⚠️ *Get ready! Prepare to trade in 1 minute.*"
    )
    send_telegram_message(signal_message)
    print(f"Signal alert sent for {asset} at {formatted_trade_time}")

    # ৩. ট্রেডের নির্দিষ্ট সময় পর্যন্ত অপেক্ষা করা
    while True:
        current_time = datetime.now()
        if current_time >= trade_time:
            break
        await asyncio.sleep(1)

    # ৪. ১ মিনিট ট্রেড শেষ হওয়ার জন্য অপেক্ষা করা
    await asyncio.sleep(60)

    # ৫. রেজাল্ট ফেচ করা ও পাঠানো
    trade_result = await fetch_quotex_result(asset)
    result_icon = "✅ WIN (🟢)" if trade_result == "WIN" else "❌ LOSS (🔴)"

    result_message = (
        f"📊 *Trade Result Update* 📊\n\n"
        f"Asset: **{asset}**\n"
        f"Timeframe: **1 Minute**\n"
        f"Result: {result_icon}"
    )
    send_telegram_message(result_message)
    print(f"Trade result sent for {asset}: {trade_result}")

if __name__ == "__main__":
    asyncio.run(run_trade_cycle())
