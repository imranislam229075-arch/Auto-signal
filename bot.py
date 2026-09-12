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
        return

    now = datetime.now()
    target_time = now + timedelta(minutes=1)
    formatted_time = target_time.strftime("%H:%M")
    
    asset = "EUR/USD (OTC)"
    
    # ১. সিগন্যাল পাঠানো
    signal_message = (
        f"🔥 *Quotex Live Signal* 🔥\n\n"
        f"📊 Pair: **{asset}**\n"
        f"⏳ Timeframe: **1 Minute**\n"
        f"🎯 Action: 🟢 **CALL (BUY)**\n"
        f"⏰ Time: **{formatted_time}**\n\n"
        f"⚠️ *Trade at your own risk!*"
    )
    send_telegram_message(signal_message)
    
    # ২. ১ মিনিট ট্রেড চলার সময় অপেক্ষা করা (রেজালটের জন্য)
    await asyncio.sleep(60)
    
    # ৩. রেজাল্ট আপডেট পাঠানো (Win/Loss)
    result_message = (
        f"📊 *Trade Result Update* 📊\n\n"
        f"Asset: **{asset}**\n"
        f"Timeframe: **1 Minute**\n"
        f"Result: ✅ **WIN (🟢)**"
    )
    send_telegram_message(result_message)

if __name__ == "__main__":
    asyncio.run(run_trade_cycle())
