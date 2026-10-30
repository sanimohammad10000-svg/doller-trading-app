import requests
import json
import os

class TelegramNotifier:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'telegram_config.json')
        self.token = None
        self.chat_id = None
        self.enabled = False
        self._load_config()

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
                    self.token = config.get("bot_token", "")
                    self.chat_id = config.get("chat_id", "")
                    if self.token and self.chat_id and "YOUR_" not in self.token:
                        self.enabled = True
        except Exception as e:
            print(f"[NOTIFIER] Error loading Telegram config: {e}")

    def send_message(self, message: str):
        if not self.enabled:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"[NOTIFIER] Failed to send Telegram message: {e}")
