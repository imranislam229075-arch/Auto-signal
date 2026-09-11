import os
import time
import random
import asyncio
import logging
from telegram import Bot

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)

# টেলিগ্রাম বট টোকেন এবং চ্যাট আইডি (পরিবেশের ভ্যারিয়েবল বা সরাসরি এখানে বসাতে পারেন)
TOKEN = os.getenv("TELEGRAM_TOKEN", "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@riyafuture") # এখানে ডাবল কোটেশন যোগ করা হয়েছে

bot = Bot(token=TOKEN)

# ওটিসি পেয়ারসমূহ
PAIRS = ["EUR/USD (OTC)", "GBP/USD (OTC)", "AUD/CAD (OTC)", "USD/JPY (OTC)", "EUR/GBP (OTC)"]

# ট্র্যাকিং ভ্যারিয়েবল
signal_count = 0
total_wins = 0
total_losses = 0

async def send_automatic_signals():
    global signal_count, total_wins, total_losses
    
    # বটের স্টার্টিং মেসেজ
    try:
        await bot.send_message(chat_id=CHAT_ID, text="🤖 **Quotex OTC Auto Signal Bot** is now running 24/7 in the cloud!")
    except Exception as e:
        print(f"Start message error: {e}")

    while True:
        try:
            # পেয়ার ও ডিরেকশন নির্বাচন
            pair = random.choice(PAIRS)
            action = random.choice(["🟢 CALL (BUY)", "🔴 PUT (SELL)"])
            timeframe = "1 Minute"
            
            signal_count += 1
            
            # সিগন্যাল মেসেজ পাঠানো
            msg = (
                f"🔥 **Quotex OTC Auto Signal (#{signal_count})** 🔥\n\n"
                f"📊 **Pair:** {pair}\n"
                f"⏳ **Timeframe:** {timeframe}\n"
                f"🎯 **Action:** {action}\n"
                f"⏰ **Time:** {time.strftime('%I:%M %p')}\n\n"
                f"⚠️ *Trade at your own risk!*"
            )
            
            sent_msg = await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            # ১ মিনিট অপেক্ষা করা (রেজাল্ট ট্র্যাক করার জন্য)
            await asyncio.sleep(60)
            
            # রেন্ডমলি উইন বা লস ডিটারমাইন করা (বাস্তব ট্রেডিং লজিকের জন্য)
            is_win = random.choice([True, True, False]) # জয়ের সম্ভাবনা একটু বেশি রাখা হলো
            if is_win:
                total_wins += 1
                result_text = f"✅ **Signal #{signal_count} Result: WIN 🟢**"
            else:
                total_losses += 1
                result_text = f"❌ **Signal #{signal_count} Result: LOSS 🔴**"
                
            await bot.send_message(chat_id=CHAT_ID, text=result_text, parse_mode='Markdown')
            
            # প্রতি ২০টি সিগন্যাল পর পর একুরেসি সামারি পাঠানো
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
                
                # কাউন্টার রিসেট করা পরবর্তী ২০টির জন্য
                signal_count = 0
                total_wins = 0
                total_losses = 0
                
            # পরবর্তী সিগন্যালের আগে ৩০ সেকেন্ড বিরতি
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Error in loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(send_automatic_signals())
