import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL = "@f1nieuws"
RSS_URL = "https://www.f1news.ru/export/news.xml"

# Получаем новости
request = urllib.request.Request(
    RSS_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(request, timeout=20) as response:
    data = response.read()

root = ET.fromstring(data)

# Берём первую свежую новость
item = root.find(".//item")

if item is None:
    print("Новости не найдены")
    raise SystemExit

title = item.findtext("title", "Без заголовка")
link = item.findtext("link", "")

message = f"🏎️ {title}\n\nИсточник: F1News.ru\n{link}"

# Отправляем в Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

data = urllib.parse.urlencode({
    "chat_id": CHANNEL,
    "text": message
}).encode()

urllib.request.urlopen(url, data=data, timeout=20)

print("Новость отправлена:", title)
