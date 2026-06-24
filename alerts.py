import requests
from bs4 import BeautifulSoup
import time
import os
import logging
from datetime import datetime

# Configuration
EPRA_URL = "https://www.epra.go.ke/services/fuel-prices/"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 3600 # Check every hour

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class FuelAlertSystem:
    def __init__(self):
        self.last_prices = None

    def fetch_prices(self):
        """Scrapes fuel prices from the EPRA website."""
        try:
            logging.info("Checking EPRA for price updates...")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(EPRA_URL, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # EPRA usually publishes prices in a table or a specific container
            table = soup.find('table')
            if not table:
                return None
            
            rows = table.find_all('tr')
            prices = {}
            # Simplified parsing logic for Nairobi prices
            for row in rows[1:5]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    town = cols[0].text.strip()
                    super_petrol = cols[1].text.strip()
                    if "Nairobi" in town:
                        prices['Super'] = super_petrol
                        prices['Diesel'] = cols[2].text.strip() if len(cols) > 2 else "N/A"
                        prices['Kerosene'] = cols[3].text.strip() if len(cols) > 3 else "N/A"
            
            return prices
        except Exception as e:
            logging.error(f"Scraping error: {e}")
            return None

    def send_telegram_alert(self, prices):
        """Sends the price update via Telegram Bot API."""
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            logging.warning("Telegram credentials not configured.")
            return

        message = (
            f"⛽ *EPRA Fuel Price Update* ⛽\n\n"
            f"📍 Nairobi Base Prices:\n"
            f"⛽ Super Petrol: KSh {prices.get('Super')}\n"
            f"🚜 Diesel: KSh {prices.get('Diesel')}\n"
            f"🕯️ Kerosene: KSh {prices.get('Kerosene')}\n\n"
            f"*Effective from current cycle.*"
        )
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()
            logging.info("Telegram alert sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send Telegram alert: {e}")

    def run(self):
        logging.info("EPRA Fuel Alert script started.")
        while True:
            current_prices = self.fetch_prices()
            
            if current_prices and current_prices != self.last_prices:
                logging.info("New price change detected!")
                self.send_telegram_alert(current_prices)
                self.last_prices = current_prices
            else:
                logging.info("No price changes or table not found.")
            
            # Only run intensive checks around the 14th of the month (standard EPRA schedule)
            day_of_month = datetime.now().day
            wait_time = CHECK_INTERVAL if 13 <= day_of_month <= 15 else 86400
            
            logging.info(f"Next check in {wait_time} seconds.")
            time.sleep(wait_time)

if __name__ == "__main__":
    bot = FuelAlertSystem()
    bot.run()
