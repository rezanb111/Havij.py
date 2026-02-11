import telebot
import sqlite3
import random
import time
import threading
import os

# --- CONFIGURATION ---
TOKEN = '8217747832:AAH4mZ4yunE96yiapKudaR3zNtH9rZIpjyU' 
ADMIN_ID = 8242274171 
TARGET_GROUP = "engwechat" 
PHOTO_URL = "https://fv5-3.files.fm/thumb_show.php?i=vtbyr62f2c&view&v=1&PHPSESSID=ee4af65bd013fecf948b6e2ba731539140ec3f3c"
DB_FILE_NAME = 'pro_group_manager.db'

bot = telebot.TeleBot(TOKEN)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, name TEXT, xp INTEGER DEFAULT 0, msgs INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_FILE_NAME)
    c = conn.cursor()
    c.execute(query, params)
    res = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

# --- HELPER: DELETE MESSAGE ---
def safe_delete(chat_id, message_id, delay=0):
    def _delete():
        if delay > 0: time.sleep(delay)
        try: bot.delete_message(chat_id, message_id)
        except: pass
    threading.Thread(target=_delete).start()

# --- AUTO BACKUP SYSTEM (Every 1 Hour) ---
def auto_backup():
    while True:
        time.sleep(3600)
        try:
            if os.path.exists(DB_FILE_NAME):
                with open(DB_FILE_NAME, 'rb') as f:
                    bot.send_document(ADMIN_ID, f, caption=f"🔄 Auto-Backup: {DB_FILE_NAME}", disable_notification=True)
        except: pass

threading.Thread(target=auto_backup, daemon=True).start()

# --- AUTO WORD CHALLENGE ---
words = ["TELEGRAM", "CRYPTO", "PYTHON", "LUXURY", "GOLDEN", "SERVER", "NETWORK"]
current_word = None
challenge_msg_id = None

def word_challenge():
    global current_word, challenge_msg_id
    while True:
        time.sleep(1800) 
        if challenge_msg_id:
            safe_delete(f"@{TARGET_GROUP}", challenge_msg_id)
            
        current_word = random.choice(words)
        scrambled = "".join(random.sample(current_word, len(current_word)))
        try:
            msg = bot.send_message(f"@{TARGET_GROUP}", f"🏆 **WORD CHALLENGE!**\nUnscramble to win **20 XP**:\n\n✨ `{scrambled}` ✨", disable_notification=True, parse_mode='Markdown')
            challenge_msg_id = msg.message_id
        except: pass

threading.Thread(target=word_challenge, daemon=True).start()

# --- COMMANDS ---

@bot.message_handler(commands=['backup'])
def manual_backup(message):
    if message.from_user.id == ADMIN_ID:
        try:
            with open(DB_FILE_NAME, 'rb') as f:
                bot.send_document(ADMIN_ID, f, caption="📦 Manual Backup", disable_notification=True)
        except: pass
    safe_delete(message.chat.id, message.message_id)

@bot.message_handler(commands=['top'])
def leaderboard(message):
    safe_delete(message.chat.id, message.message_id)
    rows = db_query("SELECT name, xp FROM users ORDER BY xp DESC LIMIT 30", fetch=True)
    res = "🏆 **ELITE LEADERBOARD** 🏆\n" + "—"*20 + "\n"
    for i, row in enumerate(rows, 1):
        name = row[0] if row[0] else "User"
        res += f"{i}. {name} » `{row[1]}` XP\n"
    bot.send_message(message.chat.id, res, parse_mode='Markdown', disable_notification=True)

@bot.message_handler(commands=['me', 'status', 'start'])
def my_status(message):
    safe_delete(message.chat.id, message.message_id)
    user = db_query("SELECT xp, msgs FROM users WHERE user_id=?", (message.from_user.id,), fetch=True)
    if not user:
        db_query("INSERT OR IGNORE INTO users (user_id, name, xp, msgs) VALUES (?, ?, 0, 0)", 
                 (message.from_user.id, message.from_user.first_name))
        xp, msgs = 0, 0
    else: xp, msgs = user[0]

    caption = (f"⚜️ **LUXURY STATUS** ⚜️\n\n👤 **User:** {message.from_user.first_name}\n✨ **XP:** `{xp}`\n✉️ **Msgs:** `{msgs}`\n━━━━━━━━━━━━━━\n👑 *@{TARGET_GROUP}*")
    try:
        bot.send_photo(message.chat.id, PHOTO_URL, caption=caption, parse_mode='Markdown', disable_notification=True)
    except:
        bot.send_message(message.chat.id, caption, parse_mode='Markdown', disable_notification=True)

@bot.message_handler(commands=['send'])
def admin_transfer(message):
    safe_delete(message.chat.id, message.message_id)
    if message.from_user.id != ADMIN_ID or not message.reply_to_message: return
    try:
        amount = int(message.text.split()[1])
        db_query("UPDATE users SET xp=xp+? WHERE user_id=?", (amount, message.reply_to_message.from_user.id))
        bot.send_message(message.chat.id, f"✅ Admin gifted `{amount}` XP!", disable_notification=True)
    except: pass

@bot.message_handler(commands=['dice'])
def dice_game(message):
    safe_delete(message.chat.id, message.message_id)
    dice_msg = bot.send_dice(message.chat.id, disable_notification=True)
    
    def process_dice():
        time.sleep(4)
        if dice_msg.dice.value >= 4:
            db_query("UPDATE users SET xp=xp+20 WHERE user_id=?", (message.from_user.id,))
            res = bot.send_message(message.chat.id, "🔥 WIN! +20 XP", disable_notification=True)
        else:
            db_query("UPDATE users SET xp=xp-10 WHERE user_id=?", (message.from_user.id,))
            res = bot.send_message(message.chat.id, "💀 LOSS! -10 XP", disable_notification=True)
        
        safe_delete(message.chat.id, dice_msg.message_id, delay=5)
        safe_delete(message.chat.id, res.message_id, delay=5)

    threading.Thread(target=process_dice).start()

@bot.message_handler(func=lambda m: current_word and m.text and m.text.upper() == current_word)
def check_answer(message):
    global current_word, challenge_msg_id
    db_query("UPDATE users SET xp=xp+20 WHERE user_id=?", (message.from_user.id,))
    win = bot.send_message(message.chat.id, f"🎉 {message.from_user.first_name} won 20 XP!", disable_notification=True)
    
    safe_delete(message.chat.id, message.message_id, delay=5)
    safe_delete(message.chat.id, win.message_id, delay=5)
    if challenge_msg_id: safe_delete(message.chat.id, challenge_msg_id, delay=5)
    
    current_word = None
    challenge_msg_id = None

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    db_query("INSERT OR IGNORE INTO users (user_id, name, xp, msgs) VALUES (?, ?, 0, 0)", 
             (message.from_user.id, message.from_user.first_name))
    if message.chat.type != 'private':
        db_query("UPDATE users SET xp=xp+2, msgs=msgs+1, name=? WHERE user_id=?", 
                 (message.from_user.first_name, message.from_user.id))

bot.infinity_polling()
