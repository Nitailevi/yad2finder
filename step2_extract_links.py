from playwright.sync_api import sync_playwright

URL = "https://www.yad2.co.il/vehicles/private-cars?price=0-15000&year=2012-2016"
CANDIDATES = ['a[href*="/item"]', 'a[href*="item.php"]', 'a[data-id]']

def absolutize(href: str) -> str:
    """link to absolute URL"""
    return href if href.startswith("http") else "https://www.yad2.co.il" + href

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  
    page = browser.new_page(locale="he-IL")
    page.goto(URL, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except:
        pass

   # Scroll to load more items (down 4 times)
    for _ in range(4):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        page.wait_for_timeout(1200)

    links = set()
    for sel in CANDIDATES:
        for a in page.query_selector_all(sel):
            href = (a.get_attribute("href") or "").strip()
            if href and ("/ad/" in href or "/item" in href or "item.php" in href):
                links.add(absolutize(href))

    print(f"found {len(links)} links:")
    for u in sorted(links):
        print(u)

    browser.close()
