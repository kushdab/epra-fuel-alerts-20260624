# EPRA Fuel Alerts Kenya

Automated script that monitors the Energy and Petroleum Regulatory Authority (EPRA) website for fuel price changes (typically monthly on the 14th) and sends alerts via Telegram.

## Configuration
Requires environment variables:
- `TELEGRAM_TOKEN`: Your BotFather token.
- `TELEGRAM_CHAT_ID`: Your target chat or channel ID.

## Installation
```bash
pip install -r requirements.txt
python alerts.py
```