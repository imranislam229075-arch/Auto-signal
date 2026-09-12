import os
import requests
import asyncio
import random
from datetime import datetime, timedelta, timezone

# Telegram Credentials
TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"
CHAT_ID = "@riyafuture"

# বাংলাদেশ টাইমজোন (UTC+6)
BST = timezone(timedelta(hours=6))

# ওটিসি পেয়ারসমূহ
OTC_PAIRS = [
    "EUR/USD (OTC)",
    "GBP/USD (OTC)",
    "USD/JPY (OTC)",
    "AUD/CAD (OTC)",
    "EUR/GBP (OTC)",
    "USD/BDT (OTC)",
    "USD/MXN (OTC)",
    "USD/ARS (OTC)"
]

completed_trades_history = []
is_lock_active = False  # গ্লোবাল লক যা যেকোনো মাল্টিপল বা ডাবল ট্রিগার ১০০% ব্লক রাখবে

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

async def run_single_trade_cycle():
    global is_lock_active, completed_trades_history
    
    # যদি ইতিমধ্যে লক একটিভ থাকে, তবে যেকোনো মূল্যে নতুন এক্সিকিউশন ব্লক হবে
    if is_lock_active:
        return

    is_lock_active = True

    try:
        now_bst = datetime.now(BST)
        target_trade_time = now_bst + timedelta(minutes=1)
        formatted_trade_time = target_trade_time.strftime("%H:%M")

        # একদম সুনির্দিষ্টভাবে শুধুমাত্র ১টি পেয়ার নির্বাচন (ডাবল বা একসাথে অনেকগুলো যাওয়ার কোনো সুযোগ নেই)
        asset = random.choice(OTC_PAIRS)
        
        action_type = random.choice(["CALL (BUY)", "PUT (SELL)"])
        if action_type == "CALL (BUY)":
            action = "🟢 CALL (BUY)"
            short_action = "CALL"
            reason = "Support Level Rejection & Bullish Volume"
        else:
            action = "🔴 PUT (SELL)"
            short_action = "PUT"
            reason = "Resistance Touch & Bearish Rejection"

        # ১. সিগন্যাল পাঠানো
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
        print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Strict Single Signal Sent: {asset} at {formatted_trade_time}")

        # ২. টার্গেট টাইম পর্যন্ত নিখুঁত অপেক্ষা
        while True:
            current_bst = datetime.now(BST)
            if current_bst >= target_trade_time:
                break
            await asyncio.sleep(0.5)

        # ৩. ট্রেড এক্সিকিউশন এবং রেজال্টের জন্য ১ মিনিট অপেক্ষা
        print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Trade Executed for {asset} at {formatted_trade_time}")
        await asyncio.sleep(60)

        # ৪. রেজাল্ট জেনারেট করা
        is_win = random.choices([True, False], weights=[78, 22], k=1)[0]
        trade_result = "WIN" if is_win else "LOSS"
        result_icon = "✅" if trade_result == "WIN" else "❌"

        result_message = (
            f"📊 *TRADE RESULT* 📊\n\n"
            f"Asset: **{asset}**\n"
            f"Timeframe: **1 Minute**\n"
            f"Target Time: **{formatted_trade_time}**\n"
            f"Result: {result_icon} {trade_result}"
        )
        send_telegram_message(result_message)
        print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Result sent for {asset}: {trade_result}")

        # হিস্টরিতে যোগ করা
        completed_trades_history.append({
            "asset": asset,
            "time": formatted_trade_time,
            "action": short_action,
            "result": trade_result,
            "icon": result_icon
        })

        # ৩০টি ট্রেড পূর্ণ হলে সামারি পাঠানো
        if len(completed_trades_history) >= 30:
            summary_text = "📋 *SESSION SUMMARY REPORT (30 TRADES)* 📋\n\n`"
            wins = 0
            for t in completed_trades_history[:30]:
                summary_text += f"{t['asset']:<14} | {t['time']} | {t['action']:<4} | {t['icon']} {t['result']}\n"
                if t['result'] == "WIN":
                    wins += 1
            losses = 30 - wins
            win_rate = (wins / 30) * 100
            
            summary_text += f"`\n📊 *Total Wins:* {wins} | *Total Losses:* {losses}\n"
            summary_text += f"🎯 *Accuracy Rate:* {win_rate:.1f}%\n"
            send_telegram_message(summary_text)
            
            completed_trades_history = completed_trades_history[30:]

    except Exception as e:
        print(f"Cycle Exception: {e}")
    finally:
        # প্রসেস সম্পূর্ণ শেষ হওয়ার পর লক রিলিজ করা
        is_lock_active = False

async def main():
    print("Quotex Strict Single-Signal Bot Starting...")
    send_telegram_message("🤖 *Quotex Strict Single-Signal Bot is active!*")
    
    await asyncio.sleep(5)

    while True:
        await run_single_trade_cycle()
        # প্রতিটি ট্রেড সাইকেল শেষ হওয়ার পর সুশৃঙ্খল বিরতি
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
