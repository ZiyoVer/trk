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
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def fetch(endpoint):
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

    print("Statistika yig'ilmoqda...")
    data = fetch("/statistics")
    if data and data.get('items'):
        it = data['items']
        def yig(key):
            return round(sum(x.get(key, 0) or 0 for x in it), 1)
        sana = (it[0].get('createdAt') or '')[:10]
        suffix = f"(butun O'zbekiston bo'yicha jami, {sana} holatiga ko'ra)"

        stat_items = [
            ("Qancha kafolat berilgan? Nechta tadbirkorga kafolat berilgan?",
             "guaranteeCount", "guaranteeAmaunt", "Kafolat"),
            ("Qancha kredit berilgan? Nechta kredit ajratilgan?",
             "loanCount", "loanAmaunt", "Kredit"),
            ("Qancha kompensatsiya berilgan? Qancha foiz qoplangan?",
             "compensationCount", "compensationAmaunt", "Kompensatsiya"),
            ("Resurs ajratish bo'yicha qancha loyiha bo'lgan?",
             "resourceAllocationCount", "resourceAllocationAmaunt", "Resurs ajratish"),
            ("Ipoteka bo'yicha qancha loyiha moliyalashtirilgan?",
             "mortgageCount", "mortgageAmaunt", "Ipoteka"),
            ("Ulushli moliyalashtirish bo'yicha qancha loyiha bo'lgan?",
             "shareCount", "shareAmaunt", "Ulushli moliyalashtirish"),
        ]
        for q_title, ck, ak, label in stat_items:
            all_data.append({
                "type": "statistics",
                "title": q_title,
                "content": f"{label}: {yig(ck)} ta loyiha, {yig(ak)} mlrd so'm {suffix}."
            })
        all_data.append({
            "type": "statistics",
            "title": "TRK statistik ko'rsatkichlari (barcha xizmatlar bo'yicha umumiy raqamlar)",
            "content": (
                f"TRK milliy statistikasi {suffix}: "
                f"Kafolat {yig('guaranteeCount')} ta ({yig('guaranteeAmaunt')} mlrd so'm), "
                f"Kredit {yig('loanCount')} ta ({yig('loanAmaunt')} mlrd so'm), "
                f"Kompensatsiya {yig('compensationCount')} ta ({yig('compensationAmaunt')} mlrd so'm), "
                f"Resurs ajratish {yig('resourceAllocationCount')} ta ({yig('resourceAllocationAmaunt')} mlrd so'm), "
                f"Ipoteka {yig('mortgageCount')} ta ({yig('mortgageAmaunt')} mlrd so'm), "
                f"Ulushli moliyalashtirish {yig('shareCount')} ta ({yig('shareAmaunt')} mlrd so'm)."
            )
        })
        print(f"  {len(stat_items)+1} ta statistika yozuvi ({len(it)} viloyatdan yig'ildi)")

    with open('trk_knowledge.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Jami {len(all_data)} ta yozuv trk_knowledge.json ga saqlandi")

    for t in ['page', 'news', 'document', 'vacancy', 'statistics']:
        count = len([d for d in all_data if d['type'] == t])
        print(f"   {t}: {count} ta")

    return all_data


if __name__ == "__main__":
    scrape()
