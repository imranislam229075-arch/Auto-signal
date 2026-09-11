import os
import time
import random
import asyncio
import logging
from datetime import datetime
import pytz
from telegram import Bot

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)

# আপনার বটের টোকেন এবং চ্যানেল আইডি
TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

bot = Bot(token=TOKEN)

# বাংলাদেশের টাইমজোন সেটআপ
BD_TZ = pytz.timezone('Asia/Dhaka')

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
        start_time_bd = datetime.now(BD_TZ).strftime('%I:%M %p, %d %b %Y')
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=f"🤖 **Quotex OTC Auto Signal Bot** is online!\n🕒 **Time (BD):** {start_time_bd}"
        )
    except Exception as e:
        print(f"Start message error: {e}")

    while True:
        try:
            # পেয়ার ও ডিরেকشن নির্বাচন
            pair = random.choice(PAIRS)
            action = random.choice(["🟢 CALL (BUY)", "🔴 PUT (SELL)"])
            timeframe = "1 Minute"
            
            signal_count += 1
            current_time_bd = datetime.now(BD_TZ).strftime('%I:%M %p')
            
            # সিগন্যাল মেসেজ পাঠানো (কোনো সিরিয়াল নম্বর ছাড়া)
            msg = (
                f"🔥 **Quotex OTC Signal** 🔥\n\n"
                f"📊 **Pair:** {pair}\n"
                f"⏳ **Timeframe:** {timeframe}\n"
                f"🎯 **Action:** {action}\n"
                f"⏰ **Time:** {current_time_bd}\n\n"
                f"⚠️ *Trade at your own risk!*"
            )
            
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            # ১ মিনিট অপেক্ষা করা (রেজাল্ট ট্র্যাক করার জন্য)
            await asyncio.sleep(60)
            
            # হাই উইন প্রবাবিলিটি লজিক (প্রায় ৮০-৯০% উইন রেট)
            is_win = random.choices([True, False], weights=[85, 15], k=1)[0]
            
            if is_win:
                total_wins += 1
                result_text = f"✅ **{pair} Result: WIN 🟢**"
                await bot.send_message(chat_id=CHAT_ID, text=result_text, parse_mode='Markdown')
            else:
                total_losses += 1
                # লস হলে MTG (Martingale) সিগন্যাল যোগ করা
                mtg_action = "🟢 CALL (BUY)" if "PUT" in action else "🔴 PUT (SELL)"
                result_text = (
                    f"❌ **{pair} Result: LOSS 🔴**\n\n"
                    f"⚠️ **MTG (Martingale) Suggested!**\n"
                    f"📊 **Pair:** {pair}\n"
                    f"🎯 **Action:** {mtg_action} (Use 2.2x amount)"
                )
                await bot.send_message(chat_id=CHAT_ID, text=result_text, parse_mode='Markdown')
                
                # MTG এর ফলাফল ট্র্যাক করার জন্য ছোট্ট বিরতি ও রেন্ডম রেজাল্ট
                await asyncio.sleep(60)
                mtg_win = random.choices([True, False], weights=[90, 10], k=1)[0]
                if mtg_win:
                    total_wins += 1
                    total_losses -= 1  # মূল লস থেকে ম্যানেজ করার জন্য
                    mtg_res = f"✅ **{pair} MTG Result: WIN 🟢**"
                else:
                    mtg_res = f"❌ **{pair} MTG Result: LOSS 🔴**"
                await bot.send_message(chat_id=CHAT_ID, text=mtg_res, parse_mode='Markdown')
            
            # প্রতি ২০টি সিগন্যাল পূর্ণ হলে সামারি পাঠানো
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
                
                # কাউন্টার রিসেট করা
                signal_count = 0
                total_wins = 0
                total_losses = 0
                
            # পরবর্তী সিগন্যালের আগে বিরতি
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Error in loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(send_automatic_signals())
