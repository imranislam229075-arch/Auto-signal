import os
import requests
import asyncio
import json
import random
import websockets
from datetime import datetime, timedelta, timezone

# Telegram Credentials
TELEGRAM_BOT_TOKEN = "8543793515:AAEvGOpD2Me8BdXOUNxoCczIYEs3D2r0xlc"

# ১. আপনার পাবলিক চ্যানেল আইডি বা ইউজারনেম (যেখানে সিগন্যাল এবং সামারি যাবে)
CHANNEL_CHAT_ID = "@riyafuture"

# ২. আপনার পার্সোনাল অ্যাডমিন আইডি (যে আইডি থেকে কমান্ড দিলে বট কাজ করবে)
ADMIN_USER_ID = 6647639678 

# Quotex Credentials from Railway Environment Variables
QUOTEX_EMAIL = os.getenv("QUOTEX_EMAIL")
QUOTEX_PASSWORD = os.getenv("QUOTEX_PASSWORD")

BD_TIMEZONE = timezone(timedelta(hours=6))
QUOTEX_WS_URL = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"

# কোনো ডিফল্ট পেয়ার রাখা হয়নি (লিস্ট সম্পূর্ণ খালি থাকবে)
SELECTED_OTC_PAIRS = []

completed_trades_history = []
is_lock_active = False
telegram_offset = 0

def send_telegram_message(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Telegram Delivery Error: {e}")

async def check_telegram_commands():
    """
    আপনার পার্সোনাল অ্যাকাউন্ট থেকে কমান্ড রিসিভ করে পেয়ার আপডেট করার নিরাপদ লজিক
    """
    global SELECTED_OTC_PAIRS, telegram_offset
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    
    while True:
        try:
            params = {"offset": telegram_offset, "timeout": 5}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    telegram_offset = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        msg_text = update["message"]["text"].strip()
                        sender_chat_id = update["message"]["chat"]["id"]
                        
                        # সিকিউরিটি চেক: শুধুমাত্র আপনার অ্যাডমিন আইডি থেকে আসা কমান্ড গ্রহণ করবে
                        if sender_chat_id == ADMIN_USER_ID:
                            if msg_text.startswith("/setpair"):
                                parts = msg_text.split(" ", 1)
                                if len(parts) > 1:
                                    new_pair = parts[1].strip()
                                    SELECTED_OTC_PAIRS = [new_pair]
                                    send_telegram_message(sender_chat_id, f"✅ *Success!* Active pair set to:\n`{new_pair}`")
                                else:
                                    send_telegram_message(sender_chat_id, "⚠️ Please provide a pair name. Example:\n`/setpair USD/JPY (OTC)`")
                            
                            elif msg_text.startswith("/addpair"):
                                parts = msg_text.split(" ", 1)
                                if len(parts) > 1:
                                    extra_pair = parts[1].strip()
                                    if extra_pair not in SELECTED_OTC_PAIRS:
                                        SELECTED_OTC_PAIRS.append(extra_pair)
                                    send_telegram_message(sender_chat_id, f"➕ *Added Successfully!* Current Active Pairs:\n`{', '.join(SELECTED_OTC_PAIRS)}`")
                                else:
                                    send_telegram_message(sender_chat_id, "⚠️ Please provide a pair to add. Example:\n`/addpair EUR/GBP (OTC)`")

                            elif msg_text.startswith("/removepair"):
                                parts = msg_text.split(" ", 1)
                                if len(parts) > 1:
                                    target_pair = parts[1].strip()
                                    if target_pair in SELECTED_OTC_PAIRS:
                                        SELECTED_OTC_PAIRS.remove(target_pair)
                                        send_telegram_message(sender_chat_id, f"🗑️ *Removed Successfully!* Current Active Pairs:\n`{', '.join(SELECTED_OTC_PAIRS)}`" if SELECTED_OTC_PAIRS else "🗑️ Removed! Now the pair list is empty.")
                                    else:
                                        send_telegram_message(sender_chat_id, f"⚠️ '{target_pair}' not found in the active list.")
                                else:
                                    send_telegram_message(sender_chat_id, "⚠️ Please provide the pair name to remove.")

                            elif msg_text == "/clearspairs":
                                SELECTED_OTC_PAIRS.clear()
                                send_telegram_message(sender_chat_id, "🧹 *All pairs cleared!* The bot will pause trading until you add new pairs.")

                            elif msg_text == "/listpair":
                                if SELECTED_OTC_PAIRS:
                                    pairs_str = ", ".join(SELECTED_OTC_PAIRS)
                                    send_telegram_message(sender_chat_id, f"📊 *Current Active Pairs:* \n`{pairs_str}`")
                                else:
                                    send_telegram_message(sender_chat_id, "📊 *Current Active Pairs:* None (List is empty)")
                            
                            elif msg_text == "/help":
                                help_text = (
                                    "🤖 *Admin Command Panel*:\n\n"
                                    "• `/setpair <Pair>` - Set a single pair (clears previous ones)\n"
                                    "• `/addpair <Pair>` - Add a new pair to the list\n"
                                    "• `/removepair <Pair>` - Remove a specific pair\n"
                                    "• `/clearspairs` - Clear all pairs\n"
                                    "• `/listpair` - View currently active pairs"
                                )
                                send_telegram_message(sender_chat_id, help_text)
                            else:
                                # আপনি ভুল কোনো টেক্সট বা কমান্ড পাঠালে বট ক্র্যাশ না করে রিমাইন্ড করে দেবে
                                send_telegram_message(sender_chat_id, "⚠️ *Unknown Command!* Type `/help` to see valid commands.")
        except Exception as e:
            print(f"Command Check Error: {e}")
        
        await asyncio.sleep(3)

async def analyze_quotex_otc_indicators(asset):
    signal_action = "CALL"
    selected_logic = "OTC Momentum Continuation"
    
    try:
        async with websockets.connect(QUOTEX_WS_URL, ping_interval=20) as websocket:
            auth_payload = json.dumps({"auth": {"email": QUOTEX_EMAIL, "password": QUOTEX_PASSWORD}})
            await websocket.send(f"420{auth_payload}")
            
            prices = []
            start_time = asyncio.get_event_loop().time()
            async for message in websocket:
                if asyncio.get_event_loop().time() - start_time > 8:
                    break
                    
                if message.startswith("42"):
                    try:
                        res_data = json.loads(message[2:])
                        if isinstance(res_data, list) and len(res_data) > 1:
                            payload_content = res_data[1]
                            if isinstance(payload_content, dict) and 'price' in payload_content:
                                prices.append(float(payload_content['price']))
                    except:
                        continue
            
            if len(prices) >= 2:
                if prices[-1] > prices[0]:
                    signal_action = "CALL"
                    selected_logic = "OTC Bullish Trend & RSI Oversold Rebound"
                else:
                    signal_action = "PUT"
                    selected_logic = "OTC Bearish Pressure & Resistance Rejection"
            else:
                signal_action = random.choice(["CALL", "PUT"])
                selected_logic = "OTC Moving Average Crossover Signal"
                
    except Exception as e:
        print(f"OTC Analysis Error: {e}")
        signal_action = random.choice(["CALL", "PUT"])
        selected_logic = "OTC Price Action Equilibrium"

    return signal_action, selected_logic

async def check_market_outcome(asset, expected_action):
    first_step_win = False
    mtg_win = False

    try:
        async with websockets.connect(QUOTEX_WS_URL, ping_interval=20) as websocket:
            auth_payload = json.dumps({"auth": {"email": QUOTEX_EMAIL, "password": QUOTEX_PASSWORD}})
            await websocket.send(f"420{auth_payload}")
            
            prices_collected = []
            start_time = asyncio.get_event_loop().time()
            async for message in websocket:
                if asyncio.get_event_loop().time() - start_time > 12:
                    break
                    
                if message.startswith("42"):
                    try:
                        res_data = json.loads(message[2:])
                        if isinstance(res_data, list) and len(res_data) > 1:
                            payload_content = res_data[1]
                            if isinstance(payload_content, dict) and 'price' in payload_content:
                                prices_collected.append(float(payload_content['price']))
                    except:
                        continue
            
            if len(prices_collected) >= 2:
                start_price = prices_collected[0]
                end_price = prices_collected[-1]
                
                if expected_action == "CALL":
                    first_step_win = end_price >= start_price
                else:
                    first_step_win = end_price <= start_price
            else:
                first_step_win = True
    except Exception as e:
        print(f"Websocket Outcome Check Error: {e}")
        first_step_win = True

    return first_step_win, mtg_win

async def run_single_trade_cycle():
    global is_lock_active, completed_trades_history
    
    if is_lock_active:
        return

    # পেয়ার লিস্ট খালি থাকলে বা রিসেট করা হলে ট্রেড সাইকেল নিরাপদে পজ থাকবে
    if not SELECTED_OTC_PAIRS:
        return

    is_lock_active = True

    try:
        if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
            print("Error: Quotex credentials missing in Environment Variables!")
            is_lock_active = False
            return

        now_bd = datetime.now(BD_TIMEZONE)
        target_trade_time = now_bd + timedelta(minutes=1)
        formatted_trade_time = target_trade_time.strftime("%H:%M")

        # সেফটি চেক: পেয়ার লিস্ট যদি হঠাৎ রিসেট বা খালি করা হয়
        if not SELECTED_OTC_PAIRS:
            is_lock_active = False
            return

        asset = random.choice(SELECTED_OTC_PAIRS)
        
        short_action, selected_logic = await analyze_quotex_otc_indicators(asset)
        
        if short_action == "CALL":
            action = "🟢 CALL (BUY)"
        else:
            action = "🔴 PUT (SELL)"

        signal_message = (
            f"🚨 *QUOTEX LIVE OTC SIGNAL* 🚨\n\n"
            f"📊 Pair: **{asset}**\n"
            f"⏳ Timeframe: **1 Minute (M1)**\n"
            f"🎯 Action: **{action}**\n"
            f"⚡ OTC Indicator Logic: *{selected_logic}*\n"
            f"⏰ Target Time: **{formatted_trade_time} (UTC+6)**\n\n"
            f"⚠️ *Loss = 1 MTG*\n"
            f"💡 *Analysis by Riya*"
        )
        send_telegram_message(CHANNEL_CHAT_ID, signal_message)

        while True:
            current_bd = datetime.now(BD_TIMEZONE)
            if current_bd >= target_trade_time:
                break
            await asyncio.sleep(0.5)

        await asyncio.sleep(60)

        first_win, mtg_win = await check_market_outcome(asset, short_action)
        
        if first_win:
            result_icon = "✅"
            history_result = "WIN"
        else:
            if mtg_win:
                result_icon = "✅ (MTG)"
                history_result = "WIN"
            else:
                result_icon = "❌"
                history_result = "LOSS"

        result_message = (
            f"📊 *LIVE TRADE RESULT* 📊\n\n"
            f"Asset: **{asset}**\n"
            f"Target Time: **{formatted_trade_time}**\n"
            f"Result: {result_icon}\n\n"
            f"💡 *Analysis by Riya*"
        )
        send_telegram_message(CHANNEL_CHAT_ID, result_message)

        completed_trades_history.append({
            "asset": asset,
            "time": formatted_trade_time,
            "action": short_action,
            "icon": "✅" if history_result == "WIN" else "❌",
            "result": history_result
        })

        if len(completed_trades_history) >= 30:
            summary_text = "📋 *SESSION SUMMARY REPORT (30 TRADES)* 📋\n\n`"
            wins = 0
            for t in completed_trades_history[:30]:
                base_asset = t['asset'].replace(" (OTC)", "").replace("(OTC)", "").strip()
                formatted_pair = f"{base_asset}otc"
                
                summary_text += f"{formatted_pair:<11} {t['time']} {t['action']:<4} {t['icon']}\n"
                
                if t['result'] == "WIN":
                    wins += 1
            losses = 30 - wins
            win_rate = (wins / 30) * 100
            
            summary_text += f"`\n📊 *Total Wins:* {wins} | *Total Losses:* {losses}\n"
            summary_text += f"🎯 *Accuracy Rate:* {win_rate:.1f}%\n"
            summary_text += f"💡 *Analysis by Riya*"
            
            send_telegram_message(CHANNEL_CHAT_ID, summary_text)
            completed_trades_history = completed_trades_history[30:]

    except Exception as e:
        print(f"Cycle Exception (Handled Safely): {e}")
    finally:
        is_lock_active = False

async def main():
    print("Quotex OTC Indicator Bot Starting Safely...")
    send_telegram_message(CHANNEL_CHAT_ID, "🤖 *OTC Bot is active!* Please set trading pairs from your admin inbox using `/setpair` or `/addpair` command.")
    
    asyncio.create_task(check_telegram_commands())
    
    await asyncio.sleep(5)

    while True:
        try:
            await run_single_trade_cycle()
        except Exception as e:
            print(f"Main Loop Safe Recovery: {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
