import requests
import json
import os
import streamlit as st

class TelegramNotifier:
    def __init__(self):
        self.token = None
        self.chat_id = None
        self.enabled = False
        self._load_config()

    def _load_config(self):
        # 1. Try Streamlit Secrets (For Cloud)
        try:
            self.token = st.secrets["TELEGRAM_BOT_TOKEN"]
            self.chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            if self.token and self.chat_id:
                self.enabled = True
                return
        except Exception:
            pass

        # 2. Fallback to Local JSON (For Local Dev)
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'telegram_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
                    self.token = config.get("bot_token", "")
                    self.chat_id = config.get("chat_id", "")
                    if self.token and self.chat_id and "YOUR_" not in self.token:
                        self.enabled = True
        except Exception as e:
            print(f"[NOTIFIER] Error loading config: {e}")

    def send_message(self, message: str):
        if not self.enabled:
            return
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"[NOTIFIER] Failed to send message: {e}")
