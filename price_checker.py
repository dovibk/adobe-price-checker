import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = "8805380248:AAFE_tGMDpS0vd5x6aMAeziB5ga2OEliuh0"
CHAT_ID = "1071347915"

ADOBE_URL = "https://www.adobe.com/il_he/creativecloud/plans.html"
THRESHOLD = 105  # שקלים

def get_price():
    r = requests.get(ADOBE_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    price_elements = soup.find_all(string=lambda t: "NIS" in t)
    prices = []

    for p in price_elements:
        try:
            num = float(
                p.replace("NIS", "")
                 .replace("/mo", "")
                 .replace("/month", "")
                 .strip()
            )
            prices.append(num)
        except ValueError:
            continue

    return min(prices) if prices else None

def send_telegram_alert(price):
    msg = f"המחיר של Lightroom+Photoshop באתר אדובי ישראל ירד ל-{price} ש\"ח!"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def main():
    price = get_price()
    if price is not None and price < THRESHOLD:
        send_telegram_alert(price)

if __name__ == "__main__":
    main()
