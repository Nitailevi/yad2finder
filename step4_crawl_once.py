import time, random
from pathlib import Path
from playwright.sync_api import sync_playwright
from step3_seen import load_seen, save_seen
from notify_telegram import send_telegram


URL = "https://www.yad2.co.il/vehicles/cars?carFamilyType=1&manufacturer=38,46&model=10654,10514&year=2016-2019&price=9000-26000&km=-1-115000&hand=0-3"
STATE_FILE = Path("state.json")  # cookies/session persistence

def absolutize(href: str) -> str:
    """Make relative href absolute"""
    return href if href.startswith("http") else "https://www.yad2.co.il" + href

def extract_links(page):
    """Extract all ad links from the page"""
    selectors = ['a[href*="/item"]', 'a[href*="item.php"]', 'a[data-id]']
    links = set()
    for sel in selectors:
        try:
            for a in page.query_selector_all(sel):
                href = (a.get_attribute("href") or "").strip()
                if href and ("/item" in href or "item.php" in href):
                    links.add(absolutize(href))
        except Exception as e:
            print(f"[DEBUG] selector {sel} failed: {e}")
    return links

def crawl_once(url):
    with sync_playwright() as p:
        print("[DEBUG] launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)  # extra slow

        if STATE_FILE.exists():
            context = browser.new_context(
                storage_state=str(STATE_FILE),
                locale="he-IL",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0.0.0 Safari/537.36"
            )
            print("[DEBUG] loaded existing state.json")
        else:
            context = browser.new_context(
                locale="he-IL",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0.0.0 Safari/537.36"
            )
            print("[DEBUG] first run: will save state.json after")

        page = context.new_page()
        print("[DEBUG] navigating to page...")
        page.goto(url, wait_until="domcontentloaded")

        # random human delay
        time.sleep(random.uniform(5, 10))

        try:
            page.wait_for_load_state("networkidle", timeout=20000)
            print("[DEBUG] page load complete")
        except:
            print("[DEBUG] networkidle timeout, continuing anyway")

        # handle cookie/consent popup if present
        try:
            btn = page.query_selector("button:has-text('מאשר')") or page.query_selector("button:has-text('קבל')")
            if btn:
                btn.click()
                print("[DEBUG] clicked consent button")
                time.sleep(random.uniform(3, 6))
        except Exception as e:
            print(f"[DEBUG] no consent button clicked: {e}")

        # scroll down slowly, like a human
        for i in range(6):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight/6);")
            page.wait_for_timeout(random.randint(2000, 4000))  # 2–4s
            print(f"[DEBUG] scrolled step {i+1}")

        # another long pause
        time.sleep(random.uniform(5, 12))

        links = extract_links(page)
        print(f"[DEBUG] extracted {len(links)} links")

        # save session state (cookies) so captcha solved once stays valid
        context.storage_state(path=str(STATE_FILE))
        print("[DEBUG] saved state.json")

        browser.close()
        return links

if __name__ == "__main__":
    print("[DEBUG] loading seen ads...")
    seen = load_seen()

    print("[DEBUG] crawling once...")
    links = crawl_once(URL)

    new_ads = [u for u in links if u not in seen]
    print(f"Found {len(links)} total ads, {len(new_ads)} new")

if new_ads:
    print("New ads:")
    for u in new_ads:
        print("•", u)

    # Send to Telegram (split if text is long)
    body = "\n".join(new_ads)
    if len(body) <= 3800:
        send_telegram("Yad2 – new ads", body)
    else:
        # Telegram text limit ~4096; keep it safe
        chunk = []
        total = 0
        for line in new_ads:
            if total + len(line) + 1 > 3800:
                send_telegram("Yad2 – new ads", "\n".join(chunk))
                chunk, total = [], 0
            chunk.append(line); total += len(line) + 1
        if chunk:
            send_telegram("Yad2 – new ads", "\n".join(chunk))

    seen |= set(new_ads)
    save_seen(seen)
    print("[DEBUG] saved updated seen.json")
else:
    print("No new ads")
