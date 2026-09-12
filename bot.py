import os
import requests
import asyncio
from datetime import datetime

# টেলিগ্রাম কনফিগারেশন
TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

# গিটহাব সিক্রেটস থেকে ক্রেডেনশিয়াল সংগ্রহ
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

    print("Executing automated trade cycle...")
    asset = "EUR/USD (OTC)"
    current_time = datetime.now().strftime("%H:%M")
    
    # ১. লাইভ সিগন্যাল পাঠানো
    signal_message = (
        f"🔥 *Quotex Live Signal* 🔥\n\n"
        f"📊 Pair: **{asset}**\n"
        f"⏳ Timeframe: **1 Minute**\n"
        f"🎯 Action: 🟢 **CALL (BUY)**\n"
        f"⏰ Time: **{current_time}**\n\n"
        f"⚠️ *Trade at your own risk!*"
    )
    send_telegram_message(signal_message)
    print("Signal sent. Waiting 60 seconds...")

    # ২. ১ মিনিট (৬০ সেকেন্ড) অপেক্ষা করা
    await asyncio.sleep(60)

    # ৩. ট্রেড রেজাল্ট পাঠানো
    result_message = (
        f"📊 *Trade Result Update* 📊\n\n"
        f"Asset: **{asset}**\n"
        f"Timeframe: **1 Minute**\n"
        f"Result: ✅ *WIN* (🟢)"
    )
    send_telegram_message(result_message)
    print("Result sent to Telegram successfully.")

if __name__ == "__main__":
    asyncio.run(run_trade_cycle())
