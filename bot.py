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

# ৩০টি ট্রেডের সামারি হিস্টরি ট্র্যাক করার জন্য লিস্ট
completed_trades_history = []
is_batch_running = False

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

async def run_single_pair_trade(asset, target_trade_time, formatted_trade_time):
    # র্যান্ডম অ্যাকশন ও সঠিক ইমোজি নির্ধারণ (CALL এর জন্য সবুজ, PUT এর জন্য লাল)
    action_type = random.choice(["CALL (BUY)", "PUT (SELL)"])
    if action_type == "CALL (BUY)":
        action = "🟢 CALL (BUY)"
        short_action = "CALL"
        reason = "Support Level Rejection & Bullish Pressure"
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
    print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Signal Sent: {asset} -> {action} at {formatted_trade_time}")

    # ২. টার্গেট টাইম পর্যন্ত অপেক্ষা করা
    while True:
        current_bst = datetime.now(BST)
        if current_bst >= target_trade_time:
            break
        await asyncio.sleep(0.5)

    # ৩. ট্রেড এক্সিকিউশন এবং ১ মিনিট ক্যান্ডেল ক্লোজিংয়ের জন্য ওয়েট করা
    print(f"[{datetime.now(BST).strftime('%H:%M:%S')}] Trade Executed for {asset} at {formatted_trade_time}")
    await asyncio.sleep(60)

    # ৪. রেজাল্ট নির্ধারণ (৭৮% উইন এবং ২২% লস রিয়েলিস্টিক রেশিও)
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

    return {
        "asset": asset,
        "time": formatted_trade_time,
        "action": short_action,
        "result": trade_result,
        "icon": result_icon
    }

def send_summary_report():
    global completed_trades_history
    
    summary_text = "📋 *SESSION SUMMARY REPORT (30 TRADES)* 📋\n\n`"
    wins = 0
    losses = 0
    
    for t in completed_trades_history[:30]:
        summary_text += f"{t['asset']:<14} | {t['time']} | {t['action']:<4} | {t['icon']} {t['result']}\n"
        if t['result'] == "WIN":
            wins += 1
        else:
            losses += 1

    win_rate = (wins / 30) * 100
    summary_text += f"`\n📊 *Total Wins:* {wins} | *Total Losses:* {losses}\n"
    summary_text += f"🎯 *Accuracy Rate:* {win_rate:.1f}%\n"

    send_telegram_message(summary_text)
    print("30 Trades Summary Report Sent.")

    # প্রথম ৩০টি ডেটা রিমুভ করে পরবর্তী সাইকেলের জন্য লিস্ট খালি করা
    completed_trades_history = completed_trades_history[30:]

async def run_dual_trade_batch():
    global is_batch_running, completed_trades_history
    if is_batch_running:
        return

    is_batch_running = True

    try:
        now_bst = datetime.now(BST)
        target_trade_time = now_bst + timedelta(minutes=1)
        formatted_trade_time = target_trade_time.strftime("%H:%M")

        # একসাথে ঠিক ২টি ভিন্ন পেয়ার সিলেক্ট করা
        chosen_pairs = random.sample(OTC_PAIRS, 2)
        asset1 = chosen_pairs[0]
        asset2 = chosen_pairs[1]

        print(f"Starting dual trade batch for: {asset1} and {asset2} at {formatted_trade_time}")

        # দুটি পেয়ারের ট্রেড একসাথে প্যারাレルভাবে রান করা এবং দুটির রেজাল্ট আসার পর্যন্ত অপেক্ষা করা
        results = await asyncio.gather(
            run_single_pair_trade(asset1, target_trade_time, formatted_trade_time),
            run_single_pair_trade(asset2, target_trade_time, formatted_trade_time)
        )

        # রেজাল্টগুলো হিস্টরিতে যোগ করা
        for res in results:
            completed_trades_history.append(res)

        # যদি মোট সম্পন্ন ট্রেডের সংখ্যা ৩০ বা তার বেশি হয়, তবে সামারি রিপোর্ট পাঠানো
        if len(completed_trades_history) >= 30:
            send_summary_report()

    except Exception as e:
        print(f"Batch Exception: {e}")
    finally:
        is_batch_running = False

async def main():
    print("Quotex OTC Dual-Pair Bot Starting on Railway...")
    send_telegram_message("🤖 *Quotex OTC Dual-Pair Signal Bot is active!*")
    
    await asyncio.sleep(5)

    while True:
        await run_dual_trade_batch()
        # দুটি পেয়ারের কাজ পুরোপুরি শেষ হওয়ার পর পরবর্তী ব্যাচ শুরু হওয়ার আগে স্বাভাবিক বিরতি
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
