import os
import asyncio
import json
import websockets
from datetime import datetime, timezone, timedelta
from telegram import Bot

TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

bot = Bot(token=TOKEN)
QUOTEX_WS_URL = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"

async def quotex_live_listener():
    while True:
        try:
            print("Connecting to Quotex WebSocket...")
            async with websockets.connect(QUOTEX_WS_URL, ping_interval=20) as websocket:
                print("Connected to Quotex Live Market!")
                await websocket.send("40")
                
                async for message in websocket:
                    if message.startswith("42"):
                        try:
                            data = json.loads(message[2:])
                            event_type = data[0] if isinstance(data, list) else ""
                            
                            # লাইভ সিগন্যাল ট্রিগার বা লজিক এখানে কাজ করবে
                            if "ticker" in event_type:
                                bangla_time = datetime.now(timezone(timedelta(hours=6))).strftime('%I:%M %p')
                                alert_text = f"🚨 **LIVE OTC SIGNAL** 🚨\n⏰ Time: {bangla_time}\n📊 Market: Live Feed Connected"
                                await bot.send_message(chat_id=CHAT_ID, text=alert_text, parse_mode='Markdown')
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Connection error: {e}. Reconnecting...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(quotex_live_listener())
