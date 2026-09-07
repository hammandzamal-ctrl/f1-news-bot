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

# Ограничиваем длину новости
if len(description) > 500:
    description = description[:500].rsplit(" ", 1)[0] + "..."

message = f"🏎️ {title}\n\n{description}\n\n🔗 Источник: F1News.ru\n{link}"

# Ищем фотографию на странице новости
image_url = None

try:
    page_request = urllib.request.Request(
        link,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        }
    )

    with urllib.request.urlopen(page_request, timeout=20) as response:
        page = response.read().decode("utf-8", errors="ignore")

    # Вариант 1: og:image, когда property идёт перед content
    match = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        page,
        re.IGNORECASE
    )

    # Вариант 2: content идёт перед property
    if not match:
        match = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            page,
            re.IGNORECASE
        )

    # Вариант 3: name="og:image"
    if not match:
        match = re.search(
            r'<meta[^>]+(?:name|property)=["\']og:image["\'][^>]+content=["\']([^"\']+)',
            page,
            re.IGNORECASE
        )

    if match:
        image_url = html.unescape(match.group(1)).strip()

        # Если ссылка относительная — превращаем её в полную
        image_url = urllib.parse.urljoin(link, image_url)

        print("Найдена фотография:", image_url)
    else:
        print("Фотография на странице не найдена")

except Exception as e:
    print("Ошибка при поиске фото:", e)

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
