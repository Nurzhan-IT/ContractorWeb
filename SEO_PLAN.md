# SEO Plan — ContractorWebDev.com

> Домен новый, 5 статей опубликованы. Цель: органический трафик из Google.
> Дата составления: 2026-05-09

---

## Текущее состояние

**Что уже есть (хорошо):**
- Meta title/description на всех страницах
- Open Graph и Twitter Card теги
- JSON-LD схемы (Article, WebDesignAgency, FAQPage, Service, BreadcrumbList)
- Sitemap.xml через `django.contrib.sitemaps`
- robots.txt с правилами
- HTTPS + HSTS в production
- Canonical URL на всех страницах

**Критические проблемы:**
- В `templates/robots.txt` используется `{{ site_domain }}` — переменная не передаётся в контекст, строка `Sitemap:` рендерится пустой. Google не находит sitemap автоматически.
- Нет Google Search Console — Google ещё не знает о сайте.
- Нет Google Analytics 4 — нет данных о трафике.
- 5 статей — слишком мало для нового домена.
- Нет ни одной внешней ссылки (backlinks) — главный тормоз для нового домена.

---

## Приоритет 1 — Технические исправления (делать сегодня)

### 1.1 Починить robots.txt

Файл `templates/robots.txt` — строка с Sitemap рендерится пустой.

**Исправление** в `apps/landing/views.py` или где обрабатывается robots.txt — добавить `site_domain` в контекст:
```python
# Или просто захардкодить в templates/robots.txt:
Sitemap: https://contractorwebdev.com/sitemap.xml
```

Проверить после деплоя: `curl https://contractorwebdev.com/robots.txt`

### 1.2 Проверить sitemap.xml

Открыть в браузере: `https://contractorwebdev.com/sitemap.xml`

Убедиться что:
- Отдаётся XML без ошибок
- Все 5 статей присутствуют
- URL статей ведут на реальные страницы (не 404)
- `<lastmod>` заполнен корректными датами

### 1.3 Проверить canonical URL на блог-статьях

В `templates/blog/detail.html` canonical строится через `request.build_absolute_uri(request.path)`.
Убедиться что он совпадает с реальным URL статьи (не содержит query-параметры, trailing slash соответствует настройкам сайта).

---

## Приоритет 2 — Google инструменты (делать сегодня)

### 2.1 Google Search Console

1. Зайти на [search.google.com/search-console](https://search.google.com/search-console)
2. Добавить property: **Domain** (не URL prefix) → `contractorwebdev.com`
3. Верифицировать через DNS TXT-запись (рекомендуется) или HTML-файл
4. После верификации: **Sitemaps** → добавить `https://contractorwebdev.com/sitemap.xml`
5. Запросить индексацию главной страницы через **URL Inspection** → "Request Indexing"
6. Запросить индексацию каждой из 5 статей по одной

> Первое появление в поиске: обычно 2–4 недели для нового домена.

### 2.2 Google Analytics 4

1. Создать аккаунт на [analytics.google.com](https://analytics.google.com)
2. Создать GA4 Property → получить Measurement ID (вида `G-XXXXXXXXXX`)
3. Добавить в `templates/base.html` перед `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

4. Добавить тот же код в `templates/base_landing.html` и `templates/base_landing_solid_navbar.html`
5. Вынести `GOOGLE_ANALYTICS_ID` в `.env` и передавать через контекст Django (не хардкодить в шаблоне)

### 2.3 Google Business Profile (для локального SEO)

Если сайт ориентирован на конкретный город/регион:
1. Зарегистрировать на [business.google.com](https://business.google.com)
2. Указать city/region обслуживания
3. Ссылка на сайт: `https://contractorwebdev.com`
4. Это даёт трафик через Google Maps и локальные результаты

---

## Приоритет 3 — Контент (главный фактор для нового домена)

### 3.1 Сколько нужно статей

Для нового домена минимальный порог для стабильного трафика — **30–50 статей**.
5 статей недостаточно. Нужно публиковать **2–3 статьи в неделю**.

### 3.2 Стратегия ключевых слов

Целевая аудитория: подрядчики (plumbers, electricians, roofers) и клиенты ищущие их.

**Кластеры тем для блога:**

| Кластер | Примеры статей |
|---|---|
| Contractor business tips | "How to get more plumbing leads in 2025", "Contractor website must-haves" |
| Local SEO for contractors | "How electricians rank on Google Maps", "Local SEO for roofers" |
| Pricing guides | "How much does roof repair cost in [City]", "Plumbing leak repair cost guide" |
| How-to for homeowners | "When to call an emergency plumber", "Signs your electrical panel needs upgrade" |
| Technology for contractors | "Best scheduling apps for plumbers", "Online booking for contractors" |
| Seasonal content | "Preparing your home's plumbing for winter", "Spring roof inspection checklist" |

**Инструменты для подбора ключевых слов (бесплатно):**
- [Google Keyword Planner](https://ads.google.com/keywordplanner) — бесплатно с аккаунтом Google Ads
- [Ahrefs Free Keyword Generator](https://ahrefs.com/keyword-generator)
- Google Search → раздел "People also ask" и "Related searches"

### 3.3 Структура статей для SEO

Каждая статья должна:
- **Заголовок H1** содержит главный ключевой запрос
- **Длина** минимум 1000 слов, идеально 1500–2500
- **Структура**: H2/H3 подзаголовки каждые 200–300 слов
- **FAQ секция** в конце (Google любит featured snippets)
- **Внутренние ссылки** на другие статьи блога и демо-страницы
- **Meta description** вручную написан (не автогенерирован из первого абзаца)
- **Cover image** с alt-текстом содержащим ключевой запрос

### 3.4 Внутренняя перелинковка

Каждая новая статья должна ссылаться на:
- 2–3 другие статьи блога (тематически близкие)
- 1 демо-страницу (`/demo/quote/`, `/demo/booking/`, и т.д.) как CTA

В старых статьях добавить ссылки на новые.

---

## Приоритет 4 — Backlinks (ссылки на сайт)

Для нового домена backlinks — самый важный сигнал для Google. Без них ранжирование идёт очень медленно.

### 4.1 Каталоги для веб-агентств (делать сразу)

Yelp, BBB, Angi — не подходят: они для локального бизнеса с американским адресом.
Эти платформы специально для агентств по всему миру — адрес страны там не является минусом.

| Платформа | Для чего | Приоритет |
|---|---|---|
| Clutch.co | Главный каталог IT/веб агентств, клиенты активно ищут там подрядчиков | Высокий |
| DesignRush.com | Каталог агентств по нишам, есть фильтр "contractor website design" | Высокий |
| GoodFirms.co | Отзывы и рейтинги агентств, хорошо индексируется Google | Средний |
| AgencySpotter.com | Специализированный каталог веб-агентств | Средний |
| Facebook Business Page | Страница агентства со ссылкой на сайт | Низкий |

**Важно для Clutch и GoodFirms:** нужны отзывы реальных клиентов — без них профиль не ранжируется внутри платформы. Попроси первых клиентов оставить отзыв сразу после завершения проекта.

### 4.2 HARO / Help a Reporter Out

[HARO](https://www.helpareporter.com) — журналисты ищут экспертов для статей. Отвечать на запросы в нише home improvement/contractors. Ссылка в медиа = сильный backlink.

### 4.3 Гостевые статьи

Написать статьи для:
- Блогов о home improvement
- Региональных строительных ассоциаций
- SaaS-блогов для малого бизнеса

### 4.4 Resource Page Link Building

Найти страницы типа "contractor resources" или "home improvement tools" и предложить добавить ссылку на `contractorwebdev.com` как ресурс для подрядчиков.

---

## Приоритет 5 — Технические SEO улучшения в коде

### 5.1 Добавить поля в модель Article

В `apps/blog/models.py` добавить:

```python
updated_at = models.DateTimeField(auto_now=True)
seo_title = models.CharField(max_length=70, blank=True)       # кастомный title
seo_description = models.CharField(max_length=160, blank=True) # кастомный meta description
featured_image_alt = models.CharField(max_length=200, blank=True)
reading_time = models.PositiveSmallIntegerField(null=True, blank=True)  # в минутах
```

В `templates/blog/detail.html` использовать:
```html
<title>{{ article.seo_title or article.title }} | ContractorWebDev</title>
<meta name="description" content="{{ article.seo_description or article.excerpt }}">
```

### 5.2 Article Open Graph — добавить article: теги

В `templates/blog/detail.html` добавить в `<head>`:
```html
<meta property="article:published_time" content="{{ article.published_at.isoformat() }}">
<meta property="article:modified_time" content="{{ article.updated_at.isoformat() }}">
<meta property="article:section" content="{{ article.category.name }}">
<meta property="og:type" content="article">
```

### 5.3 BreadcrumbList на странице блога

В `templates/blog/index.html` добавить JSON-LD:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://contractorwebdev.com/"},
    {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://contractorwebdev.com/blog/"}
  ]
}
</script>
```

### 5.4 Скорость страниц (Core Web Vitals)

Google использует Core Web Vitals как сигнал ранжирования.

Проверить на [PageSpeed Insights](https://pagespeed.web.dev/):
- `https://contractorwebdev.com/`
- `https://contractorwebdev.com/blog/`
- Одна из статей блога

Цели: LCP < 2.5s, CLS < 0.1, FID < 100ms

Типичные проблемы Django-сайтов:
- Изображения без `loading="lazy"` и без явных width/height
- Неиспользуемый CSS/JS (Tailwind CDN загружает весь фреймворк)
- Нет кэширования статики (проверить nginx/caddy конфиг на сервере)

### 5.5 Изображения в статьях

Если в статьях используются `cover_image_url` (URL на внешние изображения):
- Лучше хранить изображения локально (в `media/blog/`) для контроля над размером и alt-текстом
- Все `<img>` теги должны иметь `alt="{{ article.featured_image_alt or article.title }}"`
- Добавить `width` и `height` атрибуты для стабильности layout (CLS)

---

## Приоритет 6 — Мониторинг и отчётность

### 6.1 Еженедельные проверки (после настройки GSC)

- Google Search Console → **Performance** → смотреть Impressions (показы) и Clicks
- GSC → **Coverage** → проверять ошибки индексации
- GSC → **Core Web Vitals** → смотреть статус страниц

### 6.2 Ключевые метрики для отслеживания

| Метрика | Инструмент | Цель (3 месяца) |
|---|---|---|
| Проиндексировано страниц | GSC → Coverage | 100% опубликованных страниц |
| Organic impressions | GSC → Performance | > 1000/месяц |
| Organic clicks | GSC → Performance | > 50/месяц |
| Average position | GSC → Performance | < 50 для целевых запросов |
| Core Web Vitals | GSC → CWV | Все страницы "Good" |

### 6.3 Инструменты (бесплатные)

| Инструмент | Для чего |
|---|---|
| [Google Search Console](https://search.google.com/search-console) | Индексация, ключевые слова, ошибки |
| [Google Analytics 4](https://analytics.google.com) | Трафик, поведение пользователей |
| [PageSpeed Insights](https://pagespeed.web.dev) | Core Web Vitals |
| [Schema Markup Validator](https://validator.schema.org) | Проверка JSON-LD |
| [Google Rich Results Test](https://search.google.com/test/rich-results) | Проверка rich snippets |
| [Ahrefs Webmaster Tools](https://ahrefs.com/webmaster-tools) | Бесплатный мониторинг backlinks (верификация через GSC) |

---

## Временная шкала

| Срок | Задачи |
|---|---|
| **День 1–2** | Починить robots.txt, настроить GSC, добавить sitemap, установить GA4 |
| **Неделя 1** | Зарегистрироваться в 5 бизнес-каталогах, написать 2 новые статьи |
| **Неделя 2–4** | Публиковать 2–3 статьи/неделю, зарегистрироваться в оставшихся каталогах |
| **Месяц 2** | Первые показы в GSC, оптимизировать статьи с низким CTR, начать guest posting |
| **Месяц 3** | Анализ: что ранжируется → писать больше похожего контента |
| **Месяц 4–6** | Устойчивый органический трафик при условии 30+ статей и 20+ backlinks |

---

## Чего реально ожидать

- **Новый домен** — Google присваивает "Google Sandbox" period: первые 3–6 месяцев рост очень медленный даже при правильном SEO.
- **Без backlinks** — статьи могут быть проиндексированы, но не ранжироваться выше страницы 3–5.
- **С регулярным контентом (2–3 статьи/неделю) + 10–15 backlinks** — первые значимые позиции появятся через 3–4 месяца.
- **Long-tail запросы** (3–5 слов) ранжируются быстрее — фокус на них в первые месяцы.

---

## Быстрый чеклист

- [x] Починить `robots.txt` (строка Sitemap)
- [x] Добавить `updated_at` поле в модель Article, сделать миграцию
- [x] Добавить `article:published_time` / `article:modified_time` OG теги
- [x] Скрыть `/demo/*` и юридические страницы от индексации (noindex)
- [x] Убрать `/demo/*` из sitemap.xml
- [x] BreadcrumbList + CollectionPage JSON-LD на странице блога
- [x] Установить Google Analytics 4 (код добавлен — добавь реальный ID в .env)
- [x] Настроить Google Search Console, добавить sitemap
- [x] Запросить индексацию всех 5 статей через GSC
- [ ] Зарегистрировать агентство на Clutch.co
- [ ] Зарегистрировать агентство на DesignRush.com
- [ ] Проверить PageSpeed Insights, устранить критические проблемы
- [ ] Написать 2 новые статьи с long-tail ключевыми словами
- [ ] Добавить внутренние ссылки между существующими 5 статьями
- [ ] Проверить JSON-LD через Rich Results Test
