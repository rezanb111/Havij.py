import telebot
import sqlite3
import random
import time
import threading
import os
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = '8521540168:AAHfrxPBhvs9e0uA4lpWakST5wPRr0eB4IM'
ADMIN_ID = 8242274171 
TARGET_GROUP = "@engwechat" # Only works here
PHOTO_URL = "https://i.ibb.co/v4mK8m7/luxury-black-gold.jpg" # Luxury Profile Background

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
        time.sleep(1800) # 30 Minutes
        current_word = random.choice(words)
        scrambled = "".join(random.sample(current_word, len(current_word)))
        try:
            bot.send_message(TARGET_GROUP, f"🏆 **WORD CHALLENGE!**\nUnscramble the word to win **20 XP**:\n\n✨ `{scrambled}` ✨")
        except: pass

threading.Thread(target=word_challenge, daemon=True).start()

# --- MIDDLEWARE (Group & Language Check) ---
@bot.message_handler(func=lambda m: m.chat.username != "engwechat" and m.chat.type != "private")
def block_others(message):
    return # Ignore other groups

# --- COMMANDS ---

@bot.message_handler(commands=['top'])
def leaderboard(message):
    rows = db_query("SELECT name, xp FROM users ORDER BY xp DESC LIMIT 10", fetch=True)
    res = "🏆 **ELITE LEADERBOARD** 🏆\n" + "—"*20 + "\n"
    for i, row in enumerate(rows, 1):
        res += f"{i}. {row[0]} » `{row[1]}` XP\n"
    bot.send_message(message.chat.id, res, parse_mode='Markdown')

@bot.message_handler(commands=['me', 'status'])
def my_status(message):
    user = db_query("SELECT xp, msgs FROM users WHERE user_id=?", (message.from_user.id,), fetch=True)
    if user:
        xp, msgs = user[0]
        caption = (f"⚜️ **LUXURY STATUS** ⚜️\n\n"
                   f"👤 **User:** {message.from_user.first_name}\n"
                   f"✨ **XP Points:** `{xp}`\n"
                   f"✉️ **Messages:** `{msgs}`\n"
                   f"━━━━━━━━━━━━━━\n"
                   f"👑 *Keep shining in @engwechat*")
        bot.send_photo(message.chat.id, PHOTO_URL, caption=caption, parse_mode='Markdown')

@bot.message_handler(commands=['send'])
def admin_transfer(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Access Denied. Only Admin can transfer XP.")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Reply to the person you want to reward.")
        return
    
    try:
        amount = int(message.text.split()[1])
        db_query("UPDATE users SET xp=xp+? WHERE user_id=?", (amount, message.reply_to_message.from_user.id))
        bot.send_message(message.chat.id, f"✅ Admin gifted `{amount}` XP to {message.reply_to_message.from_user.first_name}!")
    except:
        bot.reply_to(message, "❌ Format: `/send 100` (Reply to user)")

@bot.message_handler(commands=['dice'])
def dice_game(message):
    msg = bot.send_dice(message.chat.id)
    val = msg.dice.value
    if val >= 4:
        db_query("UPDATE users SET xp=xp+20 WHERE user_id=?", (message.from_user.id,))
        bot.reply_to(message, f"🔥 WIN! You got 20 XP.")
    else:
        db_query("UPDATE users SET xp=xp-10 WHERE user_id=?", (message.from_user.id,))
        bot.reply_to(message, f"💀 LOSS! 10 XP deducted.")

# --- WORD CHALLENGE ANSWER CHECKER ---
@bot.message_handler(func=lambda m: current_word and m.text.upper() == current_word)
def check_answer(message):
    global current_word
    db_query("UPDATE users SET xp=xp+20 WHERE user_id=?", (message.from_user.id,))
    bot.reply_to(message, f"🎉 CORRECT! {message.from_user.first_name} won 20 XP!")
    current_word = None

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    db_query("INSERT OR IGNORE INTO users (user_id, name, xp, msgs) VALUES (?, ?, 0, 0)", 
             (message.from_user.id, message.from_user.first_name))
    db_query("UPDATE users SET xp=xp+2, msgs=msgs+1, name=? WHERE user_id=?", 
             (message.from_user.first_name, message.from_user.id))

print("--- LUXURY ACTIVY BOT IS ONLINE ---")
bot.infinity_polling()
