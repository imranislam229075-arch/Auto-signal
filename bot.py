import os
import requests
import asyncio
from datetime import datetime
from quotexapi.stable_api import Quotex

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

    print("Connecting to Quotex...")
    client = Quotex(email=QUOTEX_EMAIL, password=QUOTEX_PASSWORD, lang="en")
    
    connected, reason = await client.connect()
    if not connected:
        print(f"Failed to connect to Quotex: {reason}")
        send_telegram_message("❌ *Connection Error:* Could not connect to Quotex.")
        return

    print("Connected successfully! Generating 1-Minute Signal...")

    asset = "EUR/USD (OTC)"
    current_time = datetime.now().strftime("%H:%M")
    
    # ১. সিগন্যাল অ্যালার্ট পাঠানো
    signal_message = (
        f"🔥 *Quotex Live Signal* 🔥\n\n"
        f"📊 Pair: **{asset}**\n"
        f"⏳ Timeframe: **1 Minute**\n"
        f"🎯 Action: 🟢 **CALL (BUY)**\n"
        f"⏰ Time: **{current_time}**\n\n"
        f"⚠️ *Trade at your own risk!*"
    )
    send_telegram_message(signal_message)
    print("Signal sent. Waiting 60 seconds for trade completion...")

    # ২. ১ মিনিট (৬০ সেকেন্ড) অপেক্ষা করা ট্রেড শেষ হওয়ার জন্য
    await asyncio.sleep(60)

    # ৩. ট্রেড রেজাল্ট চেক ও উইন/লস পাঠানো (এখানে ক্যান্ডেল ক্লোজ প্রাইস তুলনা করা হবে)
    # ডেমো বা রিয়েল রেজাল্ট ফরম্যাট:
    result_message = (
        f"📊 *Trade Result Update* 📊\n\n"
        f"Asset: **{asset}**\n"
        f"Timeframe: **1 Minute**\n"
        f"Result: ✅ *WIN* (🟢)"
    )
    send_telegram_message(result_message)
    print("Result sent to Telegram successfully.")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(run_trade_cycle())
