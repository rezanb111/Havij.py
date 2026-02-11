import telebot
import sqlite3
import random
import time
import threading

# --- CONFIGURATION ---
TOKEN = '8217747832:AAH4mZ4yunE96yiapKudaR3zNtH9rZIpjyU' 
ADMIN_ID = 8242274171 
TARGET_GROUP = "engwechat" 
PHOTO_URL = "https://i.ibb.co/v4mK8m7/luxury-black-gold.jpg"

bot = telebot.TeleBot(TOKEN)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('shul_mirza.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, name TEXT, xp INTEGER DEFAULT 0, msgs INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect('shul_mirza.db')
    c = conn.cursor()
    c.execute(query, params)
    res = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

# --- AUTO WORD CHALLENGE (Every 30 Mins) ---
words = ["TELEGRAM", "CRYPTO", "PYTHON", "LUXURY", "GOLDEN", "SERVER", "NETWORK"]
current_word = None

def word_challenge():
    global current_word
    while True:
        time.sleep(1800) 
        current_word = random.choice(words)
        scrambled = "".join(random.sample(current_word, len(current_word)))
        try:
            bot.send_message(f"@{TARGET_GROUP}", f"🏆 **WORD CHALLENGE!**\nUnscramble the word to win **20 XP**:\n\n✨ `{scrambled}` ✨")
        except: pass

threading.Thread(target=word_challenge, daemon=True).start()

# --- COMMANDS ---

@bot.message_handler(commands=['top'])
def leaderboard(message):
    rows = db_query("SELECT name, xp FROM users ORDER BY xp DESC LIMIT 10", fetch=True)
    res = "🏆 **ELITE LEADERBOARD** 🏆\n" + "—"*20 + "\n"
    for i, row in enumerate(rows, 1):
        name = row[0] if row[0] else "User"
        res += f"{i}. {name} » `{row[1]}` XP\n"
    bot.send_message(message.chat.id, res, parse_mode='Markdown')

@bot.message_handler(commands=['me', 'status', 'start'])
def my_status(message):
    user = db_query("SELECT xp, msgs FROM users WHERE user_id=?", (message.from_user.id,), fetch=True)
    if not user:
        db_query("INSERT OR IGNORE INTO users (user_id, name, xp, msgs) VALUES (?, ?, 0, 0)", 
                 (message.from_user.id, message.from_user.first_name))
        xp, msgs = 0, 0
    else:
        xp, msgs = user[0]

    caption = (f"⚜️ **LUXURY STATUS** ⚜️\n\n"
               f"👤 **User:** {message.from_user.first_name}\n"
               f"✨ **XP Points:** `{xp}`\n"
               f"✉️ **Messages:** `{msgs}`\n"
               f"━━━━━━━━━━━━━━\n"
               f"👑 *Keep shining in @{TARGET_GROUP}*")
    
    try:
        bot.send_photo(message.chat.id, PHOTO_URL, caption=caption, parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, caption, parse_mode='Markdown')

@bot.message_handler(commands=['send'])
def admin_transfer(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 Access Denied.")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "❌ Reply to a user.")
        return
    try:
        amount = int(message.text.split()[1])
        db_query("UPDATE users SET xp=xp+? WHERE user_id=?", (amount, message.reply_to_message.from_user.id))
        bot.send_message(message.chat.id, f"✅ Admin gifted `{amount}` XP!")
    except:
        bot.send_message(message.chat.id, "❌ Error in format.")

@bot.message_handler(commands=['dice'])
def dice_game(message):
    dice_msg = bot.send_dice(message.chat.id)
    val = dice_msg.dice.value
    time.sleep(4) # صبر برای انیمیشن تاس
    
    if val >= 4:
        db_query("UPDATE users SET xp=xp+20 WHERE user_id=?", (message.from_user.id,))
        bot.send_message(message.chat.id, f"🔥 WIN! You got 20 XP.", reply_to_message_id=message.message_id)
    else:
        db_query("UPDATE users SET xp=xp-10 WHERE user_id=?", (message.from_user.id,))
        bot.send_message(message.chat.id, f"💀 LOSS! 10 XP deducted.", reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda m: current_word and m.text and m.text.upper() == current_word)
def check_answer(message):
    global current_word
    db_query("UPDATE users SET xp=xp+20 WHERE user_id=?", (message.from_user.id,))
    bot.send_message(message.chat.id, f"🎉 CORRECT! {message.from_user.first_name} won 20 XP!")
    current_word = None

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    db_query("INSERT OR IGNORE INTO users (user_id, name, xp, msgs) VALUES (?, ?, 0, 0)", 
             (message.from_user.id, message.from_user.first_name))
    if message.chat.type != 'private':
        db_query("UPDATE users SET xp=xp+2, msgs=msgs+1, name=? WHERE user_id=?", 
                 (message.from_user.first_name, message.from_user.id))

print("--- LUXURY ACTIVY BOT IS ONLINE ---")
bot.infinity_polling()
