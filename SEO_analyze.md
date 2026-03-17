# SEO Аудит: ContractorWeb — Professional Contractor Websites

**Дата анализа:** 2026-03-15
**Фреймворк:** Django 4.2 + Jinja2 (django-jinja)
**Тип рендеринга:** SSR (Server-Side Rendering) — все страницы рендерятся на сервере, контент полностью доступен для индексации Google.

---

## 📊 Общая оценка

| Раздел | Оценка | Комментарий |
|---|---|---|
| Технические мета-теги | 4/10 | Title/description есть, но нет canonical, og:image, og:url |
| Структура заголовков | 6/10 | H1 везде есть, но landing и demo_hub без H2 |
| Технический SEO | 2/10 | Нет robots.txt, нет sitemap.xml, нет canonical |
| Изображения | 5/10 | Portfolio хорошо, остальные страницы — эмодзи без alt |
| Скорость / Core Web Vitals | 5/10 | Leaflet и slider JS грузятся на всех страницах |
| Мобильная адаптация | 9/10 | Отлично: Tailwind, mobile-first, hamburger nav |
| Структурированные данные | 0/10 | JSON-LD полностью отсутствует |
| Внутренняя перелинковка | 7/10 | Хорошая навигация, нет breadcrumbs |
| Контент и ключевые слова | 5/10 | Мало текстового контента на demo-страницах |
| Конфигурация фреймворка | 3/10 | Нет sitemap app, нет security headers |

**Итоговый балл: 46/100** — Хорошая техническая база (SSR, мобильность, alt-тексты в portfolio), но критически не хватает SEO-инфраструктуры.

---

## 🔴 Критические проблемы (Priority 1)

### P1-1: Отсутствует `robots.txt`

**Файл:** отсутствует в проекте
**Проблема:** Поисковые боты не знают, какие страницы индексировать. `/admin/` и `/api/` открыты для краулинга, что тратит crawl budget.

**Как исправить:** создать `templates/robots.txt` и добавить URL в `config/urls.py`:

```
# templates/robots.txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /api/*
Sitemap: https://yourdomain.com/sitemap.xml
```

```python
# config/urls.py — добавить:
from django.views.generic import TemplateView
path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
```

---

### P1-2: Отсутствует `sitemap.xml`

**Файл:** отсутствует (Django contrib.sitemaps установлен, но не подключён)
**Проблема:** Google не знает о существовании всех страниц без карты сайта.

**Как исправить:** подключить `django.contrib.sitemaps` (уже в `INSTALLED_APPS` через venv):

```python
# config/sitemaps.py — создать новый файл:
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'demo_hub',        # /demo/
            'quote:index',     # /demo/quote/
            'emergency:index', # /demo/emergency/
            'service_area:index',
            'portfolio:index',
            'booking:index',
        ]

    def location(self, item):
        return reverse(item)

class LandingSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return ['landing:index']

    def location(self, item):
        return reverse(item)
```

```python
# config/urls.py — добавить:
from django.contrib.sitemaps.views import sitemap
from config.sitemaps import StaticViewSitemap, LandingSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'landing': LandingSitemap,
}

path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
```

---

### P1-3: Отсутствует `<link rel="canonical">` на всех страницах

**Файл:** [templates/base.html](templates/base.html) — строки 1-37
**Проблема:** Если страница доступна по нескольким URL (с `/` и без, http vs https, www vs non-www), Google может посчитать их дублями и понизить позиции.

**Текущий код (base.html, строка 16 — после favicon):**
```html
<link rel="icon" href="data:image/svg+xml,...">
```

**Как должно быть — добавить после строки 16:**
```html
<link rel="canonical" href="{% block canonical %}{{ request.build_absolute_uri(request.path) }}{% endblock %}">
```

На страницах с пагинацией блок переопределяется:
```jinja2
{% block canonical %}https://yourdomain.com/blog/?page=1{% endblock %}
```

---

### P1-4: Отсутствует `<meta name="description">` на лендинге

**Файл:** [templates/landing/index.html](templates/landing/index.html) — строка 6
**Проблема:** Главная страница — самая важная для SEO. Без мета-описания Google сгенерирует его сам (плохо контролируемо), CTR в выдаче снизится.

**Текущий код:**
```html
<title>ContractorWeb — Professional Contractor Websites</title>
<script src="https://cdn.tailwindcss.com"></script>
```

**Как должно быть:**
```html
<title>ContractorWeb — Professional Contractor Websites</title>
<meta name="description" content="Professional websites for local contractors — plumbers, electricians, roofers. AI quote calculator, online booking, 24/7 emergency dispatch. More jobs guaranteed.">
<meta property="og:title" content="ContractorWeb — Professional Contractor Websites">
<meta property="og:description" content="Professional websites for local contractors. AI quotes, online booking, emergency dispatch. Built to bring more jobs.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://yourdomain.com/">
<meta property="og:image" content="https://yourdomain.com/static/img/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://yourdomain.com/static/img/og-image.png">
```

Лендинг не наследует `base.html` — у него отдельный `<head>`, что является причиной полного отсутствия мета-тегов.

---

### P1-5: Отсутствуют `og:image` и `og:url` на всех страницах

**Файл:** [templates/base.html](templates/base.html) — строки 9-13
**Проблема:** При шаринге в Facebook, Telegram, WhatsApp, LinkedIn страницы отображаются без превью-картинки. Конверсия по ссылкам из соцсетей падает.

**Текущий код:**
```html
<meta property="og:title" content="{% block og_title %}ContractorPro Demo{% endblock %}">
<meta property="og:description" content="{% block og_description %}...{% endblock %}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

**Как должно быть:**
```html
<meta property="og:title" content="{% block og_title %}ContractorPro Demo{% endblock %}">
<meta property="og:description" content="{% block og_description %}...{% endblock %}">
<meta property="og:type" content="website">
<meta property="og:url" content="{% block og_url %}{{ request.build_absolute_uri(request.path) }}{% endblock %}">
<meta property="og:image" content="{% block og_image %}{{ request.scheme }}://{{ request.get_host() }}/static/img/og-default.png{% endblock %}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{% block twitter_title %}ContractorPro Demo{% endblock %}">
<meta name="twitter:description" content="{% block twitter_desc %}...{% endblock %}">
<meta name="twitter:image" content="{% block twitter_image %}{{ request.scheme }}://{{ request.get_host() }}/static/img/og-default.png{% endblock %}">
```

Также нужно создать файл `static/img/og-default.png` размером 1200×630px.

---

### P1-6: Отсутствуют JSON-LD структурированные данные

**Файл:** ни один файл в `templates/`
**Проблема:** Google не может автоматически вычитать бизнес-информацию, типы услуг, рейтинги. Сниппеты в выдаче беднее. Для LocalBusiness это особенно критично.

**Минимальный набор — добавить в `base.html` перед `</body>`:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebDesignAgency",
  "name": "ContractorWeb",
  "url": "https://yourdomain.com",
  "logo": "https://yourdomain.com/static/img/logo.png",
  "description": "Professional websites for local contractors",
  "telephone": "+1-555-123-4567",
  "email": "hello@contractorweb.dev",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Austin",
    "addressRegion": "TX",
    "addressCountry": "US"
  },
  "sameAs": []
}
</script>
```

Дополнительно — на странице booking: `Service` schema, на portfolio: `ImageGallery`, на service area: `GeoShape`.

---

## 🟡 Важные улучшения (Priority 2)

### P2-1: Лендинг не наследует `base.html` — изолирован от общей SEO-инфраструктуры

**Файл:** [templates/landing/index.html](templates/landing/index.html)
**Проблема:** Лендинг — отдельный автономный HTML-файл (не наследует `base.html`). Все будущие изменения в `<head>` base.html (canonical, og:image и т.д.) не будут применяться к лендингу автоматически.

**Рекомендация:** При следующем рефакторинге лендинга рассмотреть создание `base_landing.html` с отдельным блоком `{% block title %}` и подключением всех нужных мета-тегов. Сейчас не трогать (правило CLAUDE.md: "Do not modify `landing` app").

---

### P2-2: Отсутствует H1/H2 иерархия на лендинге

**Файл:** [templates/landing/index.html](templates/landing/index.html)
**Проблема:** После H1 ("We Build Websites That Bring More Jobs to Local Contractors") нет ни одного H2. Секции Features, Portfolio, Pricing, Contact — все без заголовков H2. Google не понимает структуру страницы.

**Как должно быть:**
```html
<!-- Секция Features -->
<h2>Website Features That Convert Visitors Into Customers</h2>

<!-- Секция Portfolio -->
<h2>Websites Built for Contractors</h2>

<!-- Секция Pricing -->
<h2>Simple, Transparent Pricing</h2>

<!-- Секция Contact / CTA -->
<h2>Get Your Contractor Website Today</h2>
```

---

### P2-3: Блог — отсутствуют Open Graph и canonical теги

**Файл:** [templates/blog/base_blog.html](templates/blog/base_blog.html) — строки 1-11
**Файл:** [templates/blog/detail.html](templates/blog/detail.html) — строки 1-4
**Проблема:** `base_blog.html` имеет только `<title>` и `<meta name="description">`. Нет canonical, нет og-тегов, нет Twitter Card image.

**Текущий код `base_blog.html` строки 6-7:**
```html
<title>{% block title %}Blog | ContractorWeb{% endblock %}</title>
<meta name="description" content="{% block meta_description %}Practical tips...{% endblock %}">
```

**Как должно быть — добавить после строки 7:**
```html
<link rel="canonical" href="{% block canonical %}{{ request.build_absolute_uri(request.path) }}{% endblock %}">
<meta property="og:title" content="{% block og_title %}Blog | ContractorWeb{% endblock %}">
<meta property="og:description" content="{% block og_desc %}{% endblock %}">
<meta property="og:type" content="article">
<meta property="og:url" content="{{ request.build_absolute_uri(request.path) }}">
<meta property="og:image" content="{% block og_image %}https://yourdomain.com/static/img/og-blog.png{% endblock %}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{% block twitter_image %}https://yourdomain.com/static/img/og-blog.png{% endblock %}">
```

В `detail.html` добавить переопределение блоков:
```jinja2
{% block og_title %}{{ article.title }} | ContractorWeb Blog{% endblock %}
{% block og_desc %}{{ article.excerpt }}{% endblock %}
{% block og_image %}{{ article.cover_image_url }}{% endblock %}
{% block twitter_image %}{{ article.cover_image_url }}{% endblock %}
```

---

### P2-4: Отсутствует JSON-LD `Article` schema на статьях блога

**Файл:** [templates/blog/detail.html](templates/blog/detail.html)
**Проблема:** Статьи блога могут попасть в Rich Results Google (увеличенные карточки с датой, автором, изображением). Без schema разметки эта возможность упущена.

**Добавить в `{% block extra_head %}` в `detail.html`:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{ article.title }}",
  "description": "{{ article.excerpt }}",
  "datePublished": "{{ article.published_at.isoformat() }}",
  "dateModified": "{{ article.published_at.isoformat() }}",
  "image": "{{ article.cover_image_url }}",
  "publisher": {
    "@type": "Organization",
    "name": "ContractorWeb",
    "logo": {
      "@type": "ImageObject",
      "url": "https://yourdomain.com/static/img/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ request.build_absolute_uri() }}"
  }
}
</script>
```

---

### P2-5: Обложки статей блога без `loading="lazy"` и `width`/`height`

**Файл:** [templates/blog/detail.html](templates/blog/detail.html) — строка 71
**Проблема:** Изображения без `loading="lazy"` блокируют рендеринг; без `width`/`height` вызывают CLS (Cumulative Layout Shift).

**Текущий код:**
```html
<img src="{{ article.cover_image_url }}"
     alt="{{ article.title }}"
     class="w-full h-full object-cover">
```

**Как должно быть:**
```html
<img src="{{ article.cover_image_url }}"
     alt="{{ article.title }}"
     class="w-full h-full object-cover"
     loading="lazy"
     width="800"
     height="400">
```

---

### P2-6: `img-comparison-slider` и Leaflet загружаются глобально

**Файл:** [templates/base.html](templates/base.html) — строки 27, 154
**Проблема:** `img-comparison-slider` (8KB CSS + 40KB JS) загружается на ВСЕХ страницах, хотя нужен только на `/demo/portfolio/`. Leaflet (142KB CSS + JS) загружается на всех, хотя нужен только на `/demo/service-area/`. Это увеличивает LCP и общий размер страницы.

**Текущий код:**
```html
<!-- base.html строка 27 -->
<link rel="stylesheet" href="https://unpkg.com/img-comparison-slider@8/dist/styles.css" />
...
<!-- base.html строка 154 -->
<script type="module" src="https://unpkg.com/img-comparison-slider@8/dist/index.js"></script>
```

**Как должно быть — убрать из base.html, добавить только в нужные шаблоны:**

В `base.html` убрать строки 27 и 154. В `templates/portfolio/index.html`:
```html
{% block extra_head %}
<link rel="stylesheet" href="https://unpkg.com/img-comparison-slider@8/dist/styles.css" />
{% endblock %}

{% block extra_js %}
<script type="module" src="https://unpkg.com/img-comparison-slider@8/dist/index.js"></script>
{% endblock %}
```

В `templates/service_area/index.html` аналогично для Leaflet:
```html
{% block extra_head %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
{% endblock %}

{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>
{% endblock %}
```

---

### P2-7: Нет breadcrumbs на demo-страницах

**Файл:** все шаблоны в `templates/demo/`, `templates/quote/`, `templates/emergency/` и т.д.
**Проблема:** Страницы на `/demo/quote/`, `/demo/emergency/` и др. не имеют навигационных хлебных крошек. Без них Google не понимает иерархию сайта, а пользователь не знает, где он находится.

**Добавить в начало блока `{% block content %}` на каждой demo-странице:**
```html
<nav aria-label="Breadcrumb" class="text-sm text-gray-500 mb-4">
  <ol class="flex items-center gap-2" itemscope itemtype="https://schema.org/BreadcrumbList">
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a href="/" itemprop="item" class="hover:text-gray-700"><span itemprop="name">Home</span></a>
      <meta itemprop="position" content="1">
    </li>
    <li class="text-gray-400">/</li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a href="/demo/" itemprop="item" class="hover:text-gray-700"><span itemprop="name">Demo Hub</span></a>
      <meta itemprop="position" content="2">
    </li>
    <li class="text-gray-400">/</li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <span itemprop="name">Quote Calculator</span>
      <meta itemprop="position" content="3">
    </li>
  </ol>
</nav>
```

---

### P2-8: Favicon — inline SVG, не стандартный `.ico`/`.png`

**Файл:** [templates/base.html](templates/base.html) — строка 16
**Проблема:** Inline SVG favicon работает в современных браузерах, но не поддерживается в Safari iOS и некоторых версиях Chrome для Android. Apple Touch Icon отсутствует.

**Текущий код:**
```html
<link rel="icon" href="data:image/svg+xml,<svg ...>🔧</svg>">
```

**Как должно быть — создать `static/img/favicon.png` (32×32) и:**
```html
<link rel="icon" type="image/png" sizes="32x32" href="{{ static('img/favicon-32.png') }}">
<link rel="icon" type="image/png" sizes="16x16" href="{{ static('img/favicon-16.png') }}">
<link rel="apple-touch-icon" sizes="180x180" href="{{ static('img/apple-touch-icon.png') }}">
```

---

## 🟢 Рекомендации (Priority 3)

### P3-1: Добавить `<meta name="robots">` для управления индексацией

Demo-страницы технически являются демонстрационными, а не целевыми посадочными. Следует обдуманно решить — нужна ли их индексация.

**Если demo-страницы НЕ нужно индексировать:**
```html
<!-- В base.html строка 13 — после viewport -->
<meta name="robots" content="{% block robots %}index, follow{% endblock %}">
```

**В demo-страницах переопределить:**
```jinja2
{% block robots %}noindex, follow{% endblock %}
```

**Если нужно индексировать (для SEO demo-агентства):**
```html
<meta name="robots" content="index, follow">
```

---

### P3-2: Добавить `preload` для Google Fonts (устранить render-blocking)

**Файл:** [templates/base.html](templates/base.html) — строки 19-21
**Проблема:** Google Fonts загружаются без `preconnect` — хотя `preconnect` есть, но без `dns-prefetch` как fallback для старых браузеров.

**Текущий код:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

Google Fonts уже содержит `display=swap` в URL — это хорошо. Добавить `dns-prefetch`:
```html
<link rel="dns-prefetch" href="https://fonts.googleapis.com">
<link rel="dns-prefetch" href="https://fonts.gstatic.com">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

---

### P3-3: Emoji в кнопках и иконках без `aria-label`

**Файлы:** `templates/demo_hub.html`, `templates/quote/index.html`, `templates/emergency/index.html`
**Проблема:** Скринридеры зачитывают emoji вслух ("skull", "lightning bolt"), что ухудшает доступность. Google учитывает accessibility в ранжировании.

**Пример — текущий код:**
```html
<span>💰</span> AI Quote Calculator
```

**Как должно быть:**
```html
<span aria-hidden="true">💰</span> AI Quote Calculator
```

Или полная замена:
```html
<span class="text-4xl mb-2" role="img" aria-label="Money bag icon">💰</span>
```

---

### P3-4: Внешние ссылки без `rel="noreferrer"`

**Файл:** [templates/booking/index.html](templates/booking/index.html)
**Проблема:** Ссылка на Cal.com имеет только `rel="noopener"` без `noreferrer`.

**Текущий код:**
```html
<a href="https://cal.com" target="_blank" rel="noopener">Cal.com</a>
```

**Как должно быть:**
```html
<a href="https://cal.com" target="_blank" rel="noopener noreferrer">Cal.com</a>
```

---

### P3-5: Нет `hreflang` (если планируется расширение)

Сайт только на английском — сейчас `hreflang` не нужен. Но если планируется испанская версия (актуально для contractor-аудитории в США), добавить:
```html
<link rel="alternate" hreflang="en" href="https://yourdomain.com/">
<link rel="alternate" hreflang="es" href="https://yourdomain.com/es/">
```

---

### P3-6: Добавить `FAQ` Schema.org на лендинг

На лендинге присутствует секция с вопросами (или можно добавить). FAQ Schema позволяет получить расширенные сниппеты в Google.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How long does it take to build a contractor website?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We typically deliver a complete contractor website within 5-7 business days."
      }
    }
  ]
}
</script>
```

---

### P3-7: Добавить `<meta name="keywords">` (опционально)

Google официально игнорирует keywords, но Bing и Yandex до сих пор смотрят. Если аудитория включает русскоязычных клиентов:

```html
<meta name="keywords" content="contractor website, plumber website, electrician website, roofing contractor website, local contractor web design">
```

---

## 📋 Детальный анализ по разделам

### 1. Технические теги — детальный разбор

#### `base.html` (строки 1-37) — шаблон demo-раздела

| Тег | Статус | Файл/Строка |
|---|---|---|
| `<meta charset="UTF-8">` | ✅ Есть | base.html:4 |
| `<meta name="viewport">` | ✅ Есть | base.html:5 |
| `<title>` с блоком | ✅ Есть | base.html:6 |
| `<meta name="description">` с блоком | ✅ Есть | base.html:7 |
| `og:title` | ✅ Есть | base.html:10 |
| `og:description` | ✅ Есть | base.html:11 |
| `og:type` | ✅ Есть | base.html:12 |
| `og:image` | ❌ Отсутствует | — |
| `og:url` | ❌ Отсутствует | — |
| `twitter:card` | ✅ Есть | base.html:13 |
| `twitter:image` | ❌ Отсутствует | — |
| `twitter:title` | ❌ Отсутствует | — |
| `canonical` | ❌ Отсутствует | — |
| `robots` | ❌ Отсутствует | — |
| Favicon | ⚠️ Inline SVG | base.html:16 |
| `hreflang` | N/A (монояз.) | — |

#### `landing/index.html` (строки 1-9) — отдельный файл, не наследует base.html

| Тег | Статус | Файл/Строка |
|---|---|---|
| `<meta charset>` | ✅ Есть | landing/index.html:4 |
| `<meta name="viewport">` | ✅ Есть | landing/index.html:5 |
| `<title>` | ✅ Есть | landing/index.html:6 |
| `<meta name="description">` | ❌ **ОТСУТСТВУЕТ** | — |
| Все og-теги | ❌ **ОТСУТСТВУЮТ** | — |
| canonical | ❌ **ОТСУТСТВУЕТ** | — |

#### `blog/base_blog.html` (строки 1-11) — отдельная база для блога

| Тег | Статус | Файл/Строка |
|---|---|---|
| `<title>` с блоком | ✅ Есть | base_blog.html:6 |
| `<meta name="description">` | ✅ Есть | base_blog.html:7 |
| Все og-теги | ❌ **ОТСУТСТВУЮТ** | — |
| canonical | ❌ **ОТСУТСТВУЕТ** | — |

---

### 2. Структура заголовков — детальный разбор

#### Лендинг (`landing/index.html`)
```
H1: "We Build Websites That Bring More Jobs to Local Contractors" ✅
H2: ❌ Нет
H3: ❌ Нет
```
**Проблема:** 4+ смысловых секции (Features, Portfolio, Pricing, Contact) не имеют заголовков. Google не может определить темы секций.

#### Demo Hub (`demo_hub.html`)
```
H1: "See Your Future Website in Action" ✅
H2: ❌ Нет (6 feature-карточек без подзаголовков)
```

#### Quote (`quote/index.html`)
```
H1: "Get Your Free AI-Powered Estimate" ✅
H2: ❌ Нет (форма без структурных заголовков)
```

#### Emergency (`emergency/index.html`)
```
H1: "24/7 Emergency Service" ✅
H2: "How It Works" ✅
H3: "1. Describe the Problem" ✅
H3: "2. We Alert a Pro" ✅
H3: "3. They're On the Way" ✅
```
**Оценка: Отлично — идеальная иерархия.**

#### Service Area (`service_area/index.html`)
```
H1: "Service Area Map" ✅
H2: "Do We Serve Your Area?" ✅
H3: ❌ Нет (статистика без заголовков)
```

#### Portfolio (`portfolio/index.html`)
```
H1: "Real Work. Real Results." ✅
H2: "Want us to document your project like this?" ✅
H3: ❌ Нет (проекты без подзаголовков)
```
**Рекомендация:** Добавить H3 для названий проектов в `{% for project in projects %}`.

#### Booking (`booking/index.html`)
```
H1: "Book Your Service Appointment" ✅
H2: "How It Works" ✅
H2: "Works With Your Calendar" ✅
H2: "Collect a Service Call Fee at Booking" ✅
```
**Оценка: Хорошая иерархия.**

#### Blog Detail (`blog/detail.html`)
```
H1: "{{ article.title }}" ✅  (строка 85)
H2-H6: из Markdown-контента через {{ article.content_html | safe }}
```
**Внимание:** Если markdown-контент статьи начинается с `# Heading`, это создаст второй H1. Нужно убедиться, что авторы статей используют `## H2` как первый уровень в тексте.

---

### 3. Технический SEO — детальный разбор

**robots.txt:** ❌ Файл полностью отсутствует. Краулер Google видит `/admin/` и все `/api/*` эндпоинты.

**sitemap.xml:** ❌ Полностью отсутствует. `django.contrib.sitemaps` есть в составе Django, но не подключён.

**HTTPS:** ✅ В настройках нет принудительных HTTP-ссылок. Production-конфиг предполагает HTTPS.

**URL-структура (ЧПУ):** ✅ Отличная — `/demo/quote/`, `/demo/service-area/` — читаемые, без лишних параметров.

**Trailing slash:** ✅ Django по умолчанию добавляет `/` и делает 301 редирект — всё корректно.

**404 страница:** ⚠️ Не обнаружено кастомного шаблона `404.html`. Django покажет стандартный белый экран.

**Редиректы:** ⚠️ Нет явной настройки `SECURE_SSL_REDIRECT = True` в production settings для принудительного HTTPS.

---

### 4. Изображения — детальный разбор

| Страница | Изображения | Alt-текст | lazy | width/height |
|---|---|---|---|---|
| Landing | Фоновые градиенты (CSS) | N/A | N/A | N/A |
| Demo Hub | Только emoji-иконки в span | ❌ aria-hidden нет | N/A | N/A |
| Quote | Только emoji | ❌ | N/A | N/A |
| Emergency | Только emoji | ❌ | N/A | N/A |
| Service Area | Leaflet map (canvas) | ❌ (no alt on div) | N/A | N/A |
| Portfolio | `<img slot="first">` и `<img slot="second">` | ✅ "Before: title" / "After: title" | ✅ loading="lazy" | ❌ нет |
| Booking | Calendar logos (Google, Stripe, etc.) | ✅ "Google Calendar" | — | ✅ w-8 h-8 |
| Blog Detail | `{{ article.cover_image_url }}` | ✅ alt="{{ article.title }}" | ❌ нет | ❌ нет |

**Имена файлов изображений:**
Файлы before/after хранятся в `static/img/before_after/` с именами `before_1.jpg`, `after_1.jpg`. Для SEO лучше использовать осмысленные имена: `bathroom-plumbing-repair-before.jpg`, `bathroom-plumbing-repair-after.jpg`. Но менять имена нужно в связке с обновлением fixture-данных.

**Форматы:**
JPEG используется для before/after — допустимо. WebP предпочтительнее (в 2x меньше). При загрузке изображений рекомендуется конвертировать в WebP через Pillow:
```python
from PIL import Image
img.save('output.webp', 'WebP', quality=85)
```

---

### 5. Скорость и Core Web Vitals — детальный разбор

**LCP (Largest Contentful Paint):**
- На landing: Hero-секция с большим градиентным фоном — LCP обычно это H1 или CTA-кнопка. Приемлемо.
- На portfolio: `<img-comparison-slider>` — Web Component, рендерится после JS-загрузки. Может задерживать LCP.
- Leaflet карта на service_area загружает тайлы через сеть — не влияет на LCP (не в viewport выше fold).

**CLS (Cumulative Layout Shift):**
- Portfolio images без `width`/`height` — браузер не резервирует место → CLS при загрузке.
- Demo banner (32px) смещает контент при dismiss → небольшой CLS, но управляется JS.
- Cal.com embed iframe — может вызывать CLS при загрузке.

**FID/INP:**
- Tailwind CDN (play.tailwindcss.com) генерирует CSS на лету через 30KB JS runtime — это блокирующий скрипт. В production следует использовать purged/compiled Tailwind CSS.
- img-comparison-slider как `type="module"` — не блокирует парсинг (✅).

**Блокирующие ресурсы:**
```html
<!-- base.html строка 24 — БЛОКИРУЕТ рендеринг -->
<script src="https://cdn.tailwindcss.com"></script>
```
Tailwind CDN — не async, не defer. Загружается синхронно и блокирует рендеринг страницы. В production нужен compiled CSS.

---

### 6. Мобильная адаптация — детальный разбор

**Viewport:** ✅ `<meta name="viewport" content="width=device-width, initial-scale=1.0">` — строка 5 в base.html.

**Адаптивность:** ✅ Tailwind CSS с mobile-first breakpoints (`sm:`, `md:`, `lg:`).

**Мобильная навигация:**
- ✅ Hamburger menu с ARIA (`aria-expanded`, `aria-controls`)
- ✅ Закрытие по ESC (через `nav-close` button)
- ✅ Логика в base.html (строки 159-170)

**Размеры touch-targets:**
- Кнопки nav имеют `py-3 px-3` (≈48px высота) — ✅
- Form inputs с `py-2.5 px-3` — могут быть маловаты на некоторых страницах ⚠️
- Filter buttons в portfolio: нужно проверить минимум 44×44px

**Горизонтальный скролл:**
- `overflow-x` не замечено в явном виде. Tailwind `max-w-7xl mx-auto` ограничивает ширину.
- Leaflet карта имеет фиксированную высоту `style="height:280px"` — ✅ не выходит за пределы.

---

### 7. Структурированные данные — детальный разбор

**Текущее состояние:** 0 JSON-LD на всём сайте.

**Приоритетная разметка для contractor-агентства:**

| Страница | Рекомендуемый тип Schema.org | Потенциальный эффект |
|---|---|---|
| `base.html` | `WebDesignAgency` / `Organization` | Knowledge panel в Google |
| `landing/index.html` | `Service`, `FAQPage` | Расширенные сниппеты |
| `demo/quote/` | `Service` (Repair Estimate) | Rich card |
| `demo/service-area/` | `GeoShape`, `LocalBusiness` | Local Pack |
| `demo/booking/` | `Service`, `BookingService` | Booking action |
| `demo/portfolio/` | `ImageGallery` | Image carousel |
| `blog/detail.html` | `Article`, `BreadcrumbList` | Top Stories, дата |

---

### 8. Внутренняя перелинковка — детальный разбор

**Граф ссылок:**
```
/ (Landing)
  └── /demo/          [nav + CTA "Live Demo"]
  └── /blog/          [nav]

/demo/ (Hub)
  ├── /demo/quote/    [feature card + footer nav]
  ├── /demo/emergency/ [feature card + footer nav]
  ├── /demo/service-area/ [feature card + footer nav]
  ├── /demo/portfolio/ [feature card + footer nav]
  └── /demo/booking/  [feature card + footer nav + CTA]

/demo/quote/ → /demo/booking/ [CTA "Book Now"]
/demo/emergency/ → /demo/quote/ [implied]
/blog/detail/ → /blog/ [← Back link ×2]
```

**Страницы-сироты (без входящих внутренних ссылок):**
- Отдельные статьи блога доступны только через листинг `/blog/` — нет cross-linking между статьями.
- API-эндпоинты (`/api/*`) — специально закрыты, это нормально.

**Качество anchor text:**
- ✅ "AI Quote Calculator", "Emergency 24/7 Request", "Service Area Map" — описательные
- ⚠️ "Hub", "Quote", "Emergency" в footer nav — слишком короткие, без ключевых слов
- ❌ "Get Quote" — generic CTA без контекста услуги

---

### 9. Контент и ключевые слова — детальный разбор

**Объём текста по страницам (оценочно):**

| Страница | Слов (прибл.) | Статус |
|---|---|---|
| Landing | 400-600+ | ✅ Достаточно |
| Demo Hub | ~150 | ⚠️ Граница thin content |
| Quote | ~200 | ⚠️ Граница thin content |
| Emergency | ~200 | ⚠️ Граница thin content |
| Service Area | ~100 | ❌ Thin content |
| Portfolio | ~80 | ❌ Thin content |
| Booking | ~250 | ⚠️ Граница |
| Blog articles | 500+ (если хорошо написаны) | ✅ |

**Ключевые слова в первых 100 словах:**
- Landing: "contractor", "websites", "local contractors" — ✅ присутствуют
- Demo Hub: "interactive demo", "quote calculator" — ✅
- Остальные страницы: ключевые слова есть в H1/meta, но объём текстового контента мал

**Рекомендация:** Demo-страницы — это демо-инструменты, не SEO-посадочники. Для реального продвижения нужны отдельные landing pages для каждой услуги (`/contractor-website/`, `/plumber-website/` и т.д.) с полноценным контентом.

---

### 10. Конфигурация фреймворка — детальный разбор

**Django-специфичные SEO-настройки:**

**Что хорошо:**
- SSR-рендеринг — весь контент доступен Google без JS ✅
- `LANGUAGE_CODE = 'en-us'` установлен ✅
- `TIME_ZONE = 'America/New_York'` ✅

**Что отсутствует:**
```python
# config/settings/production.py — добавить:
SECURE_SSL_REDIRECT = True           # 301 redirect HTTP → HTTPS
SECURE_HSTS_SECONDS = 31536000       # HSTS header
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**Middleware для Security Headers:**
```python
# config/settings/base.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # должен быть ПЕРВЫМ
    ...
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # X-Frame-Options: DENY
]
```

**Custom 404/500:**
```python
# config/urls.py добавить:
handler404 = 'config.views.custom_404'
handler500 = 'config.views.custom_500'
```

---

## ✅ Чеклист исправлений

### 🔴 Priority 1 — Критические (делать первыми)

- [ ] **P1-1** Создать `templates/robots.txt` и добавить URL в `config/urls.py`
- [ ] **P1-2** Подключить `django.contrib.sitemaps`, создать `config/sitemaps.py` с маппингом всех публичных страниц
- [ ] **P1-3** Добавить `<link rel="canonical">` в `templates/base.html` (строка 17)
- [ ] **P1-4** Добавить `<meta name="description">` и все og-теги в `templates/landing/index.html` (после строки 6)
- [ ] **P1-5** Добавить `og:image`, `og:url`, `twitter:image`, `twitter:title` в `templates/base.html` (строки 9-13)
- [ ] **P1-6** Добавить JSON-LD Organization/WebDesignAgency schema в `templates/base.html` (перед `</body>`)

### 🟡 Priority 2 — Важные

- [ ] **P2-1** Создать `og-default.png` (1200×630px) в `static/img/` для социальных превью
- [ ] **P2-2** Добавить H2-теги в секции лендинга (Features, Portfolio, Pricing, Contact)
- [ ] **P2-3** Добавить canonical и og-теги в `templates/blog/base_blog.html` (после строки 7)
- [ ] **P2-4** Добавить JSON-LD Article schema в `templates/blog/detail.html`
- [ ] **P2-5** Добавить `loading="lazy"` и `width`/`height` к `<img>` в `blog/detail.html:71`
- [ ] **P2-6** Перенести `img-comparison-slider` CSS/JS из `base.html` в `portfolio/index.html`
- [ ] **P2-7** Перенести Leaflet CSS/JS из глобального подключения в `service_area/index.html`
- [ ] **P2-8** Добавить breadcrumbs с microdata Schema.org на все demo-страницы
- [ ] **P2-9** Заменить inline SVG favicon на стандартные `.png` файлы + Apple Touch Icon

### 🟢 Priority 3 — Рекомендации

- [ ] **P3-1** Решить стратегию индексации demo-страниц — добавить `<meta name="robots">` блок в base.html
- [ ] **P3-2** Добавить `dns-prefetch` для Google Fonts в `base.html`
- [ ] **P3-3** Добавить `aria-hidden="true"` ко всем декоративным emoji во всех шаблонах
- [ ] **P3-4** Добавить `noreferrer` к `rel` у Cal.com ссылки в `booking/index.html`
- [ ] **P3-5** Добавить JSON-LD Article schema для blog/detail.html
- [ ] **P3-6** Добавить FAQ Schema на лендинг для получения расширенных сниппетов
- [ ] **P3-7** Добавить кастомную `templates/404.html` страницу
- [ ] **P3-8** Добавить `SECURE_SSL_REDIRECT = True` и HSTS в `config/settings/production.py`
- [ ] **P3-9** В production заменить Tailwind CDN на compiled/purged CSS для устранения render-blocking
- [ ] **P3-10** Переименовать before/after изображения с осмысленными slug-именами (`plumbing-leak-repair-before.jpg`)
- [ ] **P3-11** Конвертировать JPEG-изображения в WebP формат для ускорения загрузки
- [ ] **P3-12** Проверить авторов блога — убедиться, что markdown-контент не начинается с `# H1`
- [ ] **P3-13** Добавить cross-linking между статьями блога (связанные материалы в футере статьи)
- [ ] **P3-14** Добавить `width`/`height` атрибуты к portfolio images для предотвращения CLS

---

*Аудит выполнен на основе анализа исходного кода проекта. Google Search Console и PageSpeed Insights дадут дополнительные метрики после деплоя на production.*
