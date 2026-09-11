import os
import time
import random
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from telegram import Bot

logging.basicConfig(level=logging.INFO)

# বটের টোকেন এবং চ্যানেল আইডি
TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

bot = Bot(token=TOKEN)

# ওটিসি পেয়ারসমূহ
PAIRS = ["EUR/USD (OTC)", "GBP/USD (OTC)", "AUD/CAD (OTC)", "USD/JPY (OTC)", "EUR/GBP (OTC)"]

signal_count = 0
total_wins = 0
total_losses = 0

async def send_automatic_signals():
    global signal_count, total_wins, total_losses
    
    try:
        # বাংলাদেশের সময় (UTC + 6)
        bd_time = datetime.now(timezone(timedelta(hours=6))).strftime('%I:%M %p, %d %b %Y')
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=f"🤖 **Quotex OTC Auto Signal Bot** is online!\n🕒 **Time (BD):** {bd_time}"
        )
    except Exception as e:
        print(f"Start message error: {e}")

    while True:
        try:
            pair = random.choice(PAIRS)
            action = random.choice(["🟢 CALL (BUY)", "🔴 PUT (SELL)"])
            timeframe = "1 Minute"
            win_rate = random.randint(86, 94) # রেন্ডম হাই উইনিং পার্সেন্টেজ
            
            signal_count += 1
            
            # সিগন্যালের সময় ১ মিনিট বাড়িয়ে দেওয়া হয়েছে যাতে সাবস্ক্রাইবাররা সময়মতো ট্রেড নিতে পারে
            future_time = datetime.now(timezone(timedelta(hours=6))) + timedelta(minutes=1)
            current_time_bd = future_time.strftime('%I:%M %p')
            
            msg = (
                f"🔥 **Quotex OTC Signal** 🔥\n\n"
                f"📊 **Pair:** {pair}\n"
                f"⏳ **Timeframe:** {timeframe}\n"
                f"🎯 **Action:** {action}\n"
                f"⏰ **Time:** {current_time_bd}\n"
                f"📈 **Win Rate:** {win_rate}%\n\n"
                f"⚠️ *Trade at your own risk!*"
            )
            
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            # ট্রেড চলাকালীন ১ মিনিট অপেক্ষা
            await asyncio.sleep(60)
            
            # হাই উইন প্রবাবিলিটি লজিক (MTG ছাড়া সরাসরি রেজাল্ট)
            is_win = random.choices([True, False], weights=[85, 15], k=1)[0]
            
            if is_win:
                total_wins += 1
                result_text = f"✅ **{pair} Result: WIN 🟢**"
            else:
                total_losses += 1
                result_text = f"❌ **{pair} Result: LOSS 🔴**"
                
            await bot.send_message(chat_id=CHAT_ID, text=result_text, parse_mode='Markdown')
            
            # ২০টি সিগন্যাল পূর্ণ হলে সামারি রিপোর্ট পাঠানো
            if signal_count >= 20:
                accuracy = (total_wins / signal_count) * 100
                summary_msg = (
                    f"📊 **--- 20 SIGNALS SUMMARY REPORT ---** 📊\n\n"
                    f"🔹 **Total Signals:** {signal_count}\n"
                    f"✅ **Total Wins:** {total_wins}\n"
                    f"❌ **Total Losses:** {total_losses}\n"
                    f"🎯 **Accuracy:** {accuracy:.2f}%\n\n"
                    f"_Starting next session..._"
                )
                await bot.send_message(chat_id=CHAT_ID, text=summary_msg, parse_mode='Markdown')
                
                signal_count = 0
                total_wins = 0
                total_losses = 0
                
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Error in loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(send_automatic_signals())
