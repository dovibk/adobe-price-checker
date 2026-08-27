import os
import re
import requests
from bs4 import BeautifulSoup

# כתובת הדף הרשמי של Adobe ישראל
TARGET_URL = "https://www.adobe.com/il_en/creativecloud/photography.html"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PRICE_THRESHOLD = 70.0

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"שגיאה בשליחת הודעה לטלגרם: {e}")

def check_adobe_price():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        
        # איתור מחירים בשקלים מתוך הטקסט
        prices = re.findall(r'(\d+(?:\.\d+)?)\s*NIS', text_content.replace(',', ''))
        if not prices:
            prices = re.findall(r'NIS\s*(\d+(?:\.\d+)?)', text_content.replace(',', ''))
        
        if not prices:
            print("לא ניתן היה לחלץ את המחיר כעת.")
            return

        float_prices = [float(p) for p in prices if float(p) > 0]
        current_price = float_prices[0]

        print(f"המחיר שנמצא כעת באתר: NIS {current_price:.2f}")

        # שליחת התראה רק אם המחיר ירד ל-70 ש"ח או פחות
        if current_price <= PRICE_THRESHOLD:
            msg = f"🚨 *התראת מחיר Adobe ישראל!*\n\n"
            msg += f"💰 המחיר ירד ל- *NIS {current_price:.2f} / חודש* (מתחת לרף של {PRICE_THRESHOLD:.0f} ש\"ח)!\n\n"
            msg += f"🔗 [לחץ כאן למעבר לרכישה באתר Adobe ישראל]({TARGET_URL})"
            
            send_telegram_message(msg)

    except Exception as e:
        print(f"שגיאה בבדיקה: {e}")

if __name__ == "__main__":
    check_adobe_price()
