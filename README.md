# TRK Support Bot

Tadbirkorlikni Rivojlantirish Kompaniyasi (trk.uz) uchun AI yordamchi Telegram bot.
RAG (Retrieval-Augmented Generation) arxitekturasi bilan sayt kontentidan javob beradi.

## Eslatma (kalitlar haqida)

Bu loyiha sinov topshirig'i (test task) sifatida ishlab chiqilgan. Qulaylik uchun
keys.env faylidagi API kalitlar shartli ravishda ochiq qoldirilgan — baholovchilar
qo'shimcha sozlashsiz darhol ishga tushira olishlari uchun.

Ishlab chiqarish (production) muhitida kalitlar HECH QACHON repozitoriyga
joylashtirilmaydi. Bunda:
- keys.env .gitignore orqali yashiriladi
- Kalitlar server muhit o'zgaruvchilari (environment variables) yoki
  maxfiy boshqaruv tizimi (secrets manager) orqali beriladi

## Tezkor ishga tushirish

### 1. Klonlash

    git clone https://github.com/ZiyoVer/trk.git
    cd trk

### 2. Kutubxonalarni o'rnatish

    pip install -r requirements.txt

### 3. API kalitlar

keys.env fayli loyihada mavjud (test uchun). Agar o'zingiznikini ishlatmoqchi bo'lsangiz:

    DEEPSEEK_KEY=sizning_deepseek_kalitingiz
    TELEGRAM_TOKEN=sizning_telegram_tokeningiz

DeepSeek API key: https://platform.deepseek.com (API Keys bo'limi)

Telegram token: Telegramda @BotFather ni oching, /newbot buyrug'ini yuboring

### 4. Ma'lumotlarni yig'ish

    python scrapper.py

Natija: trk_knowledge.json (164 ta yozuv)

### 5. Botni ishga tushirish

    python bot.py

### 6. Baholash

    python evaluate.py

## Fayl tuzilmasi

    trk/
    |-- scrapper.py           # trk.uz API'dan ma'lumot yig'ish
    |-- bot.py                # Telegram bot + RAG agent
    |-- evaluate.py           # Baholash tizimi (26 ta test savol)
    |-- trk_knowledge.json    # Bilim bazasi
    |-- eval/
    |   |-- eval_results.json # Baholash natijalari
    |-- requirements.txt
    |-- keys.env              # API kalitlar (test uchun ochiq)
    |-- .gitignore
    |-- design.md             # Dizayn hujjati
    |-- readme.md

## Arxitektura

    Foydalanuvchi
        |
    Telegram Bot
        |
    Input Filter (kod, injection, spam, off-topic, media himoya)
        |
    ChromaDB Semantic Search (eng tegishli 5 dokument)
        |
    DeepSeek V4 Flash LLM (javob yaratish, streaming)
        |
    Javob -> Telegram

## Asosiy xususiyatlar

- RAG — sayt kontentidan semantic qidiruv
- Ko'p bosqichli suhbat — oldingi savollar kontekstda ishlaydi (context window)
- Xavfsizlik — prompt injection, kod yozish, spam, off-topic himoya
- Media filtri — sticker, rasm, video, audio, fayl rad etiladi
- Rate limiting — 1 daqiqada 10 ta xabar
- Markdown tozalash — toza matn
- Barqaror ishlash — try/except, bo'sh/uzun xabar himoyasi
- Baholash — 26 ta test, 4 ta metrika

## Bot buyruqlari

    /start  — botni boshlash
    /help   — yordam
    /reset  — suhbat tarixini tozalash

## Texnologiyalar

- Python 3.10+
- ChromaDB — vektorli qidiruv (all-MiniLM-L6-v2 embedding)
- DeepSeek V4 Flash — LLM
- python-telegram-bot — Telegram interfeysi
- requests — API scraping

## Baholash metrikalari

    Oddiy savollar (accuracy)     — to'g'ri javob berishi
    Tashqari savollar (rejection) — begona savollarni rad etishi
    Prompt injection (security)   — hujumlardan himoya
    Kontekst savollar (memory)    — suhbat xotirasi

Natijalarni ko'rish: python evaluate.py

## Muallif

O'ktam Ziyodullayev
- Telegram: @SSup1dat
- GitHub: github.com/ZiyoVer
