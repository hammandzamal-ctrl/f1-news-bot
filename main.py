import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL = "@f1nieuws"
RSS_URL = "https://www.f1news.ru/export/news.xml"

# Получаем RSS
request = urllib.request.Request(
    RSS_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(request, timeout=20) as response:
    rss_data = response.read()

root = ET.fromstring(rss_data)
item = root.find(".//item")

if item is None:
    print("Новости не найдены")
    raise SystemExit

title = item.findtext("title", "Без заголовка").strip()
link = item.findtext("link", "").strip()
description = item.findtext("description", "").strip()

# Очищаем описание от HTML
description = html.unescape(description)
description = re.sub(r"<[^>]+>", "", description)
description = re.sub(r"\s+", " ", description).strip()

# Делаем текст новости немного подробнее
if len(description) > 500:
    description = description[:500].rsplit(" ", 1)[0] + "..."

message = f"🏎️ {title}\n\n{description}\n\n🔗 Источник: F1News.ru\n{link}"

# Ищем фотографию на странице новости
image_url = None

try:
    page_request = urllib.request.Request(
        link,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(page_request, timeout=20) as response:
        page = response.read().decode("utf-8", errors="ignore")

    match = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        page,
        re.IGNORECASE
    )

    if match:
        image_url = html.unescape(match.group(1))

except Exception as e:
    print("Фото не найдено:", e)

# Отправляем в Telegram
if image_url:
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    data = urllib.parse.urlencode({
        "chat_id": CHANNEL,
        "photo": image_url,
        "caption": message
    }).encode()

    urllib.request.urlopen(url, data=data, timeout=30)

    print("Новость с фото отправлена:", title)

else:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHANNEL,
        "text": message
    }).encode()

    urllib.request.urlopen(url, data=data, timeout=30)

    print("Новость без фото отправлена:", title)
