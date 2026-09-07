import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html
import json

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL = "@f1nieuws"

RSS_URL = "https://www.f1news.ru/export/news.xml"
STATE_FILE = "last_news.json"


def get_news():
    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read()

    root = ET.fromstring(data)
    item = root.find(".//item")

    if item is None:
        return None

    title = item.findtext("title", "Без заголовка").strip()
    link = item.findtext("link", "").strip()
    description = item.findtext("description", "").strip()

    description = html.unescape(description)
    description = re.sub(r"<[^>]+>", "", description)
    description = re.sub(r"\s+", " ", description).strip()

    if len(description) > 600:
        description = description[:600].rsplit(" ", 1)[0] + "..."

    return {
        "title": title,
        "link": link,
        "description": description
    }


def load_last_news():
    if not os.path.exists(STATE_FILE):
        return ""

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("link", "")
    except Exception:
        return ""


def save_last_news(link):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump({"link": link}, file)


def get_image(link):
    try:
        request = urllib.request.Request(
            link,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            page = response.read().decode("utf-8", errors="ignore")

        patterns = [
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']'
        ]

        for pattern in patterns:
            match = re.search(pattern, page, re.IGNORECASE)

            if match:
                image_url = html.unescape(match.group(1))
                print("Найдена фотография:", image_url)
                return image_url

    except Exception as e:
        print("Фото не найдено:", e)

    return None


def send_news(news):
    message = (
        f"🏎️ {news['title']}\n\n"
        f"{news['description']}"
    )

    image_url = get_image(news["link"])

    if image_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        data = urllib.parse.urlencode({
            "chat_id": CHANNEL,
            "photo": image_url,
            "caption": message
        }).encode()

        urllib.request.urlopen(url, data=data, timeout=30)

        print("Новость с фото отправлена:", news["title"])

    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = urllib.parse.urlencode({
            "chat_id": CHANNEL,
            "text": message
        }).encode()

        urllib.request.urlopen(url, data=data, timeout=30)

        print("Новость без фото отправлена:", news["title"])


news = get_news()

if news is None:
    print("Новости не найдены")
    raise SystemExit

last_link = load_last_news()

if news["link"] == last_link:
    print("Эта новость уже опубликована:", news["title"])
    raise SystemExit

send_news(news)
save_last_news(news["link"])

print("Готово. Новая новость опубликована.")
