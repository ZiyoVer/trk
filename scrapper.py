"""
TRK Support Bot — Scraper
=========================
trk.uz saytining ichki API'sidan ma'lumotlarni yig'ib,
bilim bazasini (trk_knowledge.json) yaratadi.

API: https://portal-api.edcom.uz/api
Endpointlar: /pages, /news, /documents, /vacancies
"""

import requests
import json
import re
import warnings

warnings.filterwarnings('ignore')

BASE = "https://portal-api.edcom.uz/api"

HEADERS = {
    "Referer": "https://trk.uz/",
    "Origin": "https://trk.uz",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


def html_tozalash(text):
    """HTML taglarni olib tashlash"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def fetch(endpoint):
    """API'dan ma'lumot olish"""
    try:
        r = requests.get(
            f"{BASE}{endpoint}",
            headers=HEADERS,
            timeout=15,
            verify=False
        )
        if r.status_code == 200:
            return r.json()
        else:
            print(f"  {endpoint}: status {r.status_code}")
    except Exception as e:
        print(f"  Xato {endpoint}: {e}")
    return None


def scrape():
    all_data = []

    # 1. Sahifalar (xizmatlar)
    print("Sahifalar yig'ilmoqda...")
    data = fetch("/pages?pageSize=100")
    if data:
        for p in data['items']:
            all_data.append({
                "type": "page",
                "title": p['title']['uz'],
                "content": p['title']['uz']
            })
        print(f"  {len(data['items'])} ta sahifa")

    # 2. Yangiliklar (eng ko'p kontent)
    print("Yangiliklar yig'ilmoqda...")
    data = fetch("/news?pageSize=100")
    if data:
        count = 0
        for n in data['items']:
            desc = n.get('description', {}).get('uz', '')
            clean = html_tozalash(desc)
            if clean:
                all_data.append({
                    "type": "news",
                    "title": n['title']['uz'],
                    "content": clean
                })
                count += 1
        print(f"  {count} ta yangilik")

    # 3. Hujjatlar
    print("Hujjatlar yig'ilmoqda...")
    data = fetch("/documents?pageSize=100")
    if data:
        for d in data['items']:
            doc_type = d.get('documentType', {}).get('typeName', {}).get('uz', '')
            all_data.append({
                "type": "document",
                "title": d['title']['uz'],
                "content": f"{d['title']['uz']}. Hujjat turi: {doc_type}"
            })
        print(f"  {len(data['items'])} ta hujjat")

    # 4. Vakansiyalar
    print("Vakansiyalar yig'ilmoqda...")
    data = fetch("/vacancies?pageSize=100")
    if data:
        for v in data['items']:
            desc = v.get('mainDescription', {}).get('uz', '')
            name = v.get('vacanciesName', {}).get('uz', '')
            all_data.append({
                "type": "vacancy",
                "title": v['mainTitle']['uz'],
                "content": f"{name} {desc}".strip()
            })
        print(f"  {len(data['items'])} ta vakansiya")

    # Saqlash
    with open('trk_knowledge.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Jami {len(all_data)} ta yozuv trk_knowledge.json ga saqlandi")

    for t in ['page', 'news', 'document', 'vacancy']:
        count = len([d for d in all_data if d['type'] == t])
        print(f"   {t}: {count} ta")

    return all_data


if __name__ == "__main__":
    scrape()