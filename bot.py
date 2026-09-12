import os
import requests
import asyncio

# টেলিগ্রাম কনফিগারেশন
TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

# গিটহাব সিক্রেটস থেকে ক্রেডেনশিয়াল রিড করা
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
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

def main():
    if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
        print("Error: Credentials missing!")
        send_telegram_message("❌ *Error:* Quotex credentials missing in GitHub Secrets!")
        return

    print("Attempting to connect Quotex with provided credentials...")
    
    # এখানে কোটেক্স এপিআই লাইব্রেরি ইনিশিয়ালাইজ করে সিগন্যাল চেকিং লজিক বসাতে হবে
    # উদাহরণস্বরূপ একটি টেস্ট সিগন্যাল মেসেজ:
    # send_telegram_message("🔥 *Quotex Signal Test*\nStatus: Connected successfully via GitHub Actions!")

    print("Execution completed.")

if __name__ == "__main__":
    main()
