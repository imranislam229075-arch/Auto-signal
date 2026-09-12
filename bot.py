import asyncio
import os
import requests

# আপনার টেলিগ্রাম কনফিগারেশন.
TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

# গিটহাব সিক্রেটস থেকে কোটেক্সের লগইন তথ্য সংগ্রহ করা
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

async def run_quotex_bot():
    print("Initializing Quotex API client with GitHub Secrets...")
    
    if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
        print("Error: QUOTEX_EMAIL or QUOTEX_PASSWORD secrets are missing!")
        send_telegram_message("❌ *Error:* Quotex credentials (Secrets) are missing in GitHub Actions!")
        return

    # টেলিগ্রামে বট সচল হওয়ার নোটিফিকেশন পাঠানো
    send_telegram_message("🤖 *Quotex Live Signal Bot Started Successfully via GitHub Actions!*")
    
    while True:
        try:
            print("Fetching live market and chart data from Quotex...")
            
            # চার্ট বা সিগন্যাল ডেটা প্রসেসিং লজিক এখানে কাজ করবে
            # যেমন: নতুন সিগন্যাল পাওয়া গেলে টেলিগ্রামে পাঠানো:
            # send_telegram_message("📈 *OTC Signal Alert*\nAsset: EURUSD\nAction: CALL (UP)")
            
            # গিটহাব অ্যাকশনস ক্রন জব বা লুপ বজায় রাখার জন্য ইন্টারভাল
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"Error occurred in loop: {e}")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(run_quotex_bot())
