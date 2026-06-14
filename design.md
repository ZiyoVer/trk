# TRK Support Bot — Dizayn hujjati

## 1. Umumiy ko'rinish

Tadbirkorlikni Rivojlantirish Kompaniyasi (trk.uz) uchun mijozlarni qo'llab-quvvatlovchi Telegram bot. RAG (Retrieval-Augmented Generation) arxitekturasi bilan ishlaydi.

Arxitektura:

    Foydalanuvchi -> Telegram Bot -> ChromaDB qidiruv -> DeepSeek LLM -> Javob

## 2. Kontentni qanday yig'dim va tuzilmaga keltirdim

trk.uz React SPA (Single Page Application) bo'lib, oddiy HTML scraping ishlamaydi — sahifa JavaScript bilan render qilinadi. Browser DevTools Network tab orqali ichki API aniqlandi:

    Base URL: https://portal-api.edcom.uz/api

Topilgan endpointlar:

    /pages      — 9 ta xizmat sahifasi (Kafolat, Ijara, Murobaha...)
    /news       — 26 ta yangilik (to'liq HTML kontent bilan)
    /documents  — 100+ ta hujjat (PDF/DOCX fayl nomlari va sarlavhalari)
    /vacancies  — 29 ta vakansiya (to'liq tavsif bilan)

Yig'ish jarayoni (scraper.py):
- API'ga requests bilan so'rov yuboriladi
- Referer va Origin headerlar majburiy (bo'lmasa server javob bermaydi)
- SSL verify=False kerak (sertifikat zanjiri muammosi)
- HTML taglar regex bilan tozalanadi
- Natija trk_knowledge.json ga saqlanadi (164 ta yozuv)

Rad etilgan muqobillar:
- Selenium/Playwright — API topilgandan keyin keraksiz. API to'g'ridan-to'g'ri JSON beradi, tezroq va ishonchliroq.
- BeautifulSoup — sayt SPA bo'lgani uchun HTML'da kontent yo'q.
- Scrapy — kichik, bir martalik yig'ish uchun ortiqcha murakkab.

## 3. Chunking va qidiruv (retrieval)

Yondashuv: Har bir ma'lumot birligi (yangilik, sahifa, vakansiya, hujjat) alohida dokument sifatida saqlanadi. Maxsus chunking qo'llanilmadi — dokumentlar o'rtacha 200-500 so'z, bu embedding model uchun optimal hajm.

Qidiruv: ChromaDB semantic search. Har bir savol uchun eng tegishli 5 ta dokument olinadi (n_results=5) va LLM'ga kontekst sifatida beriladi.

Rad etilgan muqobillar:
- Katta matnlarni chunking qilish — dokumentlar allaqachon kichik, bo'lish shart emas.
- BM25 / keyword search — semantic search ma'no bo'yicha qidiradi, "kafolat muddati" kabi savollar uchun aniqroq.
- FAISS — kuchliroq, lekin ChromaDB soddaroq va bu hajm uchun yetarli.
- Pinecone — cloud xizmat, lokal yechim afzal (tezroq, bepul, internetga bog'liq emas).

## 4. Embedding modeli, qidiruv usuli va LLM tanlovi

Embedding: ChromaDB default modeli (all-MiniLM-L6-v2)
- Bepul va lokal ishlaydi
- 384 o'lchamli vektorlar
- O'zbek tilini qisman tushunadi
- Kechikish: 100 ms dan kam

LLM: DeepSeek V4 Flash (deepseek-chat)
- Narx: 1M input uchun 0.14$, 1M output uchun 0.28$ — bozordagi eng arzonlardan
- Kechikish: 1-3 soniya
- O'zbek tilini yaxshi tushunadi va tabiiy javob beradi
- OpenAI SDK bilan to'liq mos (faqat base_url o'zgaradi)

Kelishuvlar (tradeoffs):
- DeepSeek arzon va tez, lekin Claude yoki GPT-4 dan biroz sifati past. Support bot uchun bu yetarli.
- all-MiniLM o'zbek tilini to'liq tushunmaydi, lekin bepul va tez. Production'da multilingual-e5-large ga o'tish mumkin.
- Streaming yoqilgan — foydalanuvchi javobni tezroq ko'radi.

## 5. Tizimning asosiy zaif tomonlari va xavflari

5.1. Ma'lumot to'liqligi
- /pages endpointlari faqat sarlavha qaytaradi, to'liq matn yo'q
- PDF/DOCX hujjatlar ichidagi matn indekslanmagan
- Hal qilish: Selenium bilan sahifa kontentini olish yoki PDF parsing qo'shish

5.2. Barqarorlik
- ChromaDB xotirada (in-memory) ishlaydi — qayta ishga tushganda qayta yuklanadi
- Chat history dict'da saqlanadi — ko'p foydalanuvchida xotira o'sadi
- Hal qilish: ChromaDB persist rejimi, chat history'ni Redis yoki SQLite'ga ko'chirish

5.3. Xavfsizlik
- Prompt injection — qattiq system prompt va kalit so'z filtri bilan himoyalangan
- Spam/flood — rate limiting (1 daqiqada 5 ta xabar)
- Shaxsiy ma'lumot so'rovlari oldindan filterlanadi
- Bo'sh/juda uzun xabarlar rad etiladi

5.4. Tashqi bog'liqlik
- DeepSeek API ishlamay qolsa, bot javob bera olmaydi
- Hal qilish: try/except bilan o'ralган, fallback LLM (Groq/Gemini) qo'shish mumkin

## 6. Vaqt ko'proq bo'lsa nima qilardim

1. Selenium bilan to'liq scraping — barcha xizmat sahifalarining HTML kontentini olish
2. PDF parsing — hujjatlar ichidagi matnni ajratib bilim bazasiga qo'shish
3. Multilingual embedding — multilingual-e5-large (o'zbek tilini yaxshiroq tushunadi)
4. Feedback tizimi — har javob ostida foydali/foydasiz tugmasi
5. Admin panel — bilim bazasini boshqarish, yangi kontent qo'shish
6. Auto-refresh — scraper'ni cron bilan muntazam ishga tushirib bazani yangilab turish
7. Persist storage — ChromaDB va chat history'ni doimiy saqlash
8. Caching — ko'p so'raladigan savollarga oldindan tayyor javob
9. Monitoring — savol/javob loglari va tahlil paneli
10. Docker — bir buyruqda deploy qilish