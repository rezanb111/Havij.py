import telebot
import sqlite3
import random
import time
import threading
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = '8217747832:AAGCVz5denbuMWNNGHLQC2ltCUFdg681KAU'
ADMIN_ID = 6779342889  
GROUP_ID = -1002698203044 
bot = telebot.TeleBot(TOKEN)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('shul_mirza_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, name TEXT, xp INTEGER, msgs INTEGER, last_seen TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (key TEXT PRIMARY KEY, value INTEGER)''')
    c.execute("INSERT OR IGNORE INTO settings VALUES ('motivation', 1)")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('fun', 1)")
    conn.commit()
    conn.close()

init_db()

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect('shul_mirza_ultra.db')
    c = conn.cursor()
    c.execute(query, params)
    res = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

# --- CONTENT ---
MOTIVATION = [
    "The only way to do great work is to love what you do. 🔥",
    "Don't stop when you're tired. Stop when you're DONE! 💪",
    "Your limitation—it's only your imagination. ✨",
    "Push yourself, because no one else is going to do it for you. 🚀"
]

ROASTS = [
    "English please! And keep it civil, kiddo. 🤫",
    "I'd agree with you but then we'd both be wrong. 😏",
    "Mirror mirror on the wall, you just roasted yourself, that's all.",
    "Is that the best you can do? My Grandma roasts better than you."
]

# --- BACKGROUND TASK ---
def auto_motivation():
    while True:
        time.sleep(7200)
        res = db_query("SELECT value FROM settings WHERE key='motivation'", fetch=True)
        if res and res[0][0] == 1:
            try: bot.send_message(GROUP_ID, f"💡 **QUICK REMINDER:**\n\n{random.choice(MOTIVATION)}")
            except: pass

threading.Thread(target=auto_motivation, daemon=True).start()

# --- HANDLERS ---
@bot.message_handler(commands=['toggle'])
def toggle_feature(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, key, state = message.text.split()
            val = 1 if state.lower() == 'on' else 0
            db_query("UPDATE settings SET value=? WHERE key=?", (val, key))
            bot.reply_to(message, f"✅ System: {key} is now {'ON' if val else 'OFF'}.")
        except: bot.reply_to(message, "Usage: /toggle [motivation/fun] [on/off]")

@bot.message_handler(commands=['top', 'leaderboard'])
def leaderboard(message):
    rows = db_query("SELECT name, xp FROM users ORDER BY xp DESC LIMIT 20", fetch=True)
    res = "🏆 **TOP 20 LEGENDS** 🏆\n" + "—"*20 + "\n"
    for i, row in enumerate(rows, 1):
        res += f"{i}. {row[0]} » {row[1]} XP\n"
    bot.send_message(message.chat.id, res or "No data yet!", parse_mode='Markdown')

@bot.message_handler(commands=['status', 'report'])
def report(message):
    uid = message.from_user.id
    row = db_query("SELECT xp, msgs, last_seen FROM users WHERE user_id=?", (uid,), fetch=True)
    if row: bot.reply_to(message, f"📊 **Your Activity Report:**\n\n✨ XP: {row[0][0]}\n📩 Total Msgs: {row[0][1]}\n🕒 Last Seen: {row[0][2]}")

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    now = datetime.now().strftime("%H:%M:%S")
    db_query("INSERT OR IGNORE INTO users VALUES (?, ?, 0, 0, ?)", (message.from_user.id, message.from_user.first_name, now))
    db_query("UPDATE users SET xp=xp+5, msgs=msgs+1, last_seen=?, name=? WHERE user_id=?", 
             (now, message.from_user.first_name, message.from_user.id))
    
    text = message.text.lower()
    try:
        fun_on = db_query("SELECT value FROM settings WHERE key='fun'", fetch=True)[0][0]
        if fun_on:
            if any(w in text for w in ['fuck', 'stfu', 'fack', 'idiot']):
                bot.reply_to(message, random.choice(ROASTS))
            elif text in ['hi', 'hello', 'hey', 'yo', 'sup']:
                bot.reply_to(message, random.choice([f"Yo {message.from_user.first_name}!", "Sup legend?"]))
    except: pass

print("--- SHUL MIRZA MASTER VERSION IS LIVE ---")
bot.infinity_polling()