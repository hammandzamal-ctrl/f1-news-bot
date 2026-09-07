import os
import urllib.parse
import urllib.request

token = os.environ["TELEGRAM_TOKEN"]
chat_id = "@f1nieuws"

text = "🏎️ F1 News Bot работает! Это тестовое сообщение."

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = urllib.parse.urlencode({
    "chat_id": chat_id,
    "text": text
}).encode()

urllib.request.urlopen(url, data=data)

print("Сообщение отправлено!")
