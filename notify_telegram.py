import requests

TELEGRAM_TOKEN = "8472128023:AAF2aUHNFhpTAtH6BGLLV0D7vXva6nfSF2I"   # never share this
TELEGRAM_CHAT_ID = "6926892944"          # number from @userinfobot

def send_telegram(title: str, body: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"{title}\n\n{body}", "disable_web_page_preview": False}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    print("[DEBUG] Telegram notification sent")
