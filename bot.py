import asyncio
import json
import websockets
import requests

# আপনার টেলিগ্রাম কনফিগারেশন এখানে বসান
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

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

async def listen():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://qxbroker.com"
    }
    
    uri = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
    
    while True:
        try:
            print("Connecting to Quotex WebSocket...")
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                print("Connected to Quotex WebSocket successfully!")
                
                while True:
                    message = await websocket.recv()
                    print(f"Received data: {message}")
                    
                    # এখানে আপনার সিগন্যাল ফিল্টারিং এবং কন্ডিশন চেক করার লজিক বসাবেন
                    # উদাহরণস্বরূপ:
                    # if "signal_found" in message:
                    #     send_telegram_message("🔔 New Quotex OTC Signal!")
                    
        except Exception as e:
            print(f"Connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(listen())
    
