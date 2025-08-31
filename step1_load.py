from playwright.sync_api import sync_playwright

URL = "https://www.yad2.co.il/vehicles/private-cars?price=0-15000&year=2012-2016"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) 
    page = browser.new_page(locale="he-IL",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari")
    page.goto(URL, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except:
        pass
    print("title:", page.title())
    browser.close()


