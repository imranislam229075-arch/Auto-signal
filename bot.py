import os
import requests
import asyncio
import random
from datetime import datetime, timedelta, timezone

# Telegram Credentials
TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

# Quotex Credentials from Railway Environment Variables
QUOTEX_EMAIL = os.getenv("QUOTEX_EMAIL")
QUOTEX_PASSWORD = os.getenv("QUOTEX_PASSWORD")

# বাংলাদেশ টাইমজোন (UTC+6)
BST = timezone(timedelta(hours=6))

# ওটিসি পেয়ারসমূহ
OTC_PAIRS = [
    "EUR/USD (OTC)",
    "GBP/USD (OTC)",
    "USD/JPY (OTC)",
    "AUD/CAD (OTC)",
    "EUR/GBP (OTC)",
    "USD/BDT (OTC)"
]

# ডাবল ট্রিগার রোধ করার জন্য গ্লোবাল লক
is_signal_running = False

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
        print(f"Telegram Delivery Error: {e}")

async def run_trade_cycle():
    global is_signal_running
    if is_signal_running:
        return

    is_signal_running = True

    try:
        now_bst = datetime.now(BST)
        
        # ১ মিনিট পরের সময়কে ট্রেড এক্সিকিউশন টাইম নির্ধারণ করা
        target_trade_time = now_bst + timedelta(minutes=1)
        formatted_trade_time = target_trade_time.strftime("%H:%M")

        # পেয়ার এবং এনালাইসিস জেনারেট করা
        asset = random.choice(OTC_PAIRS)
        action_type = random.choice(["CALL (BUY)", "PUT (SELL)"])
        
        if action_type == "CALL (BUY)":
            action = "🟢 CALL (BUY)"
            reason = "Support Level Rejection & Bullish Pressure"
        else:
            action = "🔴 PUT (SELL)"
            reason = "Resistance Touch & Bearish Rejection"

        # ১. প্রফেশনাল সিগন্যাল মেসেজ পাঠানো (সঠিক ইমোজি সহ)
        signal_message = (
            f"🚨 *QUOTEX OTC SIGNAL* 🚨\n\n"
            f"📊 Pair: **{asset}**\n"
            f"⏳ Timeframe: **1 Minute (M1)**\n"
            f"🎯 Action: **{action}**\n"
            f"📈 Analysis: *{reason}*\n"
            f"⏰ Target Time: **{formatted_trade_time} (BST)**\n\n"
            f"⚠️ *Get ready for {formatted_trade_time}!*"
        )
        send_telegram_message(signal_message)
        print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Signal Sent: {asset} -> {action} at {formatted_trade_time}")

        # ২. টার্গেট টাইম পর্যন্ত নিখুঁতভাবে অপেক্ষা করা
        while True:
            current_bst = datetime.now(BST)
            if current_bst >= target_trade_time:
                break
            await asyncio.sleep(0.5)

        # ৩. ট্রেড শুরু এবং ১ মিনিট ক্যান্ডেল ক্লোজিংয়ের জন্য ওয়েট করা
        print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Trade Executed for {asset} at {formatted_trade_time}")
        await asyncio.sleep(60)

        # ৪. রিয়েলিস্টিক রেজাল্ট ক্যালকুলেশন (প্রায় ৭৮% উইন এবং ২২% লস)
        is_win = random.choices([True, False], weights=[78, 22], k=1)[0]
        
        trade_result = "WIN" if is_win else "LOSS"
        result_icon = "✅ WIN (🟢)" if trade_result == "WIN" else "❌ LOSS (🔴)"

        result_message = (
            f"📊 *TRADE RESULT* 📊\n\n"
            f"Asset: **{asset}**\n"
            f"Timeframe: **1 Minute**\n"
            f"Target Time: **{formatted_trade_time}**\n"
            f"Result: {result_icon}"
        )
        send_telegram_message(result_message)
        print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Result sent for {asset}: {trade_result}")

    except Exception as e:
        print(f"Cycle Exception: {e}")
    finally:
        is_signal_running = False

async def main():
    print("Quotex OTC Signal Bot Starting on Railway...")
    send_telegram_message("🤖 *Quotex OTC Signal Bot is active and running smoothly!*")
    
    while True:
        await run_trade_cycle()
        # সিগন্যালগুলোর মাঝে স্বাভাবিক বিরতি (২ মিনিট)
        await asyncio.sleep(120)

if __name__ == "__main__":
    asyncio.run(main())
