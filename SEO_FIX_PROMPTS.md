# SEO Fix Prompts — ContractorWeb

Серия промптов для последовательного исправления проблем из `SEO_analyze.md`.
Каждый промпт — самодостаточная задача. Выполнять в порядке приоритетов.

---

## 🔴 PRIORITY 1 — Критические исправления

---

### PROMPT-P1-1: Создать robots.txt

```
Создай файл robots.txt для Django-проекта ContractorWeb.

Проект:
- Django 4.2 + Jinja2
- Структура URL: / (лендинг), /demo/* (demo-страницы), /blog/* (блог),
  /api/* (API эндпоинты), /admin/ (Django admin)

Задачи:
1. Создай файл `templates/robots.txt` со следующим содержимым:
   - User-agent: * Allow: /
   - Disallow: /admin/
   - Disallow: /api/
   - Sitemap: https://contractorweb.dev/sitemap.xml
   (замени домен на placeholder {{ site_domain }} через Jinja2)

2. В файле `config/urls.py` добавь URL для отдачи robots.txt:
   - Импортируй TemplateView из django.views.generic
   - Добавь path('robots.txt', ...) с content_type='text/plain'
   - Вставь ПЕРЕД path('', include('landing.urls')) — последним в списке

Файлы для изменения:
- создать: templates/robots.txt
- изменить: config/urls.py
```

---

### PROMPT-P1-2: Создать sitemap.xml

```
Подключи django.contrib.sitemaps и создай sitemap.xml для проекта ContractorWeb.

Структура проекта (Django 4.2):
- apps/landing/ → URL name: 'landing:index' → /
- apps/demo/ → URL name: 'demo_hub' → /demo/
- apps/quote/ → URL name: 'quote:index' → /demo/quote/
- apps/emergency/ → URL name: 'emergency:index' → /demo/emergency/
- apps/service_area/ → URL name: 'service_area:index' → /demo/service-area/
- apps/portfolio/ → URL name: 'portfolio:index' → /demo/portfolio/
- apps/booking/ → URL name: 'booking:index' → /demo/booking/
- blog/ → URL name: 'blog:index' → /blog/

Задачи:
1. Проверь `config/settings/base.py` — убедись что 'django.contrib.sitemaps'
   есть в INSTALLED_APPS. Если нет — добавь.

2. Создай файл `config/sitemaps.py` с тремя классами:
   - LandingSitemap (priority=1.0, changefreq='monthly') — только лендинг
   - DemoSitemap (priority=0.7, changefreq='weekly') — все /demo/* страницы
   - BlogSitemap (priority=0.8, changefreq='daily') — /blog/ (без отдельных статей пока)

3. В `config/urls.py`:
   - Импортируй sitemap view и классы из config.sitemaps
   - Добавь path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap')
   - Вставь после robots.txt, перед path('', ...)

Файлы для изменения:
- создать: config/sitemaps.py
- изменить: config/urls.py
- возможно изменить: config/settings/base.py
```

---

### PROMPT-P1-3: Добавить canonical тег в base.html

```
Добавь <link rel="canonical"> в шаблон templates/base.html проекта ContractorWeb.

Контекст:
- Шаблон использует Jinja2 (НЕ Django template tags)
- В Jinja2 request доступен через контекстный процессор
- base.html строка 16: <link rel="icon" href="data:image/svg+xml,...">

Задача:
Добавь после строки 16 (после favicon link) следующий тег:

<link rel="canonical" href="{% block canonical %}{{ request.scheme }}://{{ request.get_host() }}{{ request.path }}{% endblock %}">

Требования:
- Использовать Jinja2-синтаксис ({% block %}, {{ }})
- request.path даёт чистый путь без query string — это правильно для canonical
- Блок canonical должен быть переопределяемым в дочерних шаблонах

Файлы для изменения:
- templates/base.html (после строки 16)
```

---

### PROMPT-P1-4: Добавить SEO мета-теги на лендинг

```
Добавь мета-теги SEO на главную страницу лендинга ContractorWeb.

Контекст:
- Файл: templates/landing/index.html
- Лендинг НЕ наследует base.html — это отдельный автономный HTML файл
- Файл использует Jinja2 (функция static() для статики)
- Строка 6: <title>ContractorWeb — Professional Contractor Websites</title>
- Строка 7: <script src="https://cdn.tailwindcss.com"></script>
- Домен для og:url — использовать https://contractorweb.dev (хардкод — лендинг статичный)

Задача — добавить ПОСЛЕ строки 6 (после </title>, перед <script>):

1. <meta name="description"> — описание 150-160 символов с ключевыми словами:
   "contractor", "website", "plumber", "electrician", "roofing"

2. Open Graph теги:
   - og:title (= title страницы)
   - og:description (= meta description)
   - og:type = "website"
   - og:url = "https://contractorweb.dev/"
   - og:image = "https://contractorweb.dev/static/img/og-landing.png"
   - og:image:width = "1200"
   - og:image:height = "630"

3. Twitter Card теги:
   - twitter:card = "summary_large_image"
   - twitter:title
   - twitter:description
   - twitter:image

4. Canonical:
   <link rel="canonical" href="https://contractorweb.dev/">

5. Robots:
   <meta name="robots" content="index, follow">

Файлы для изменения:
- templates/landing/index.html (после строки 6)
```

---

### PROMPT-P1-5: Добавить og:image, og:url и Twitter теги в base.html

```
Дополни Open Graph и Twitter Card теги в templates/base.html проекта ContractorWeb.

Контекст:
- Шаблон использует Jinja2
- Текущие строки 9-13 в base.html:
  <meta property="og:title" content="{% block og_title %}ContractorPro Demo{% endblock %}">
  <meta property="og:description" content="{% block og_description %}...{% endblock %}">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">

Задача — заменить строки 9-13 на расширенный блок:

1. Сохранить существующие og:title, og:description, og:type
2. Добавить og:url с Jinja2-блоком (default = current URL)
3. Добавить og:image с Jinja2-блоком (default = /static/img/og-default.png)
4. Добавить og:image:width = "1200" и og:image:height = "630"
5. Добавить twitter:title с блоком (default = то же что og_title)
6. Добавить twitter:description с блоком (default = то же что og_description)
7. Добавить twitter:image с блоком (default = то же что og:image)

Для og:url и og:image использовать:
{{ request.scheme }}://{{ request.get_host() }} как base URL

Все новые теги должны иметь Jinja2-блоки для переопределения в дочерних шаблонах.

Файлы для изменения:
- templates/base.html (строки 9-13, замена и расширение)
```

---

### PROMPT-P1-6: Добавить JSON-LD Organization schema в base.html

```
Добавь JSON-LD структурированные данные (Schema.org) в templates/base.html.

Контекст:
- Сайт ContractorWeb — агентство по созданию сайтов для local contractors
- Контакты из landing: tel:+15551234567, hello@contractorweb.dev, Austin TX
- base.html строка 193: {% block extra_js %}{% endblock %}
- base.html строка 194: </body>

Задача — добавить ПЕРЕД строкой {% block extra_js %} (т.е. перед строкой 193):

1. Блок с JSON-LD типа "WebDesignAgency":
   - @type: "WebDesignAgency"
   - name: "ContractorWeb"
   - url: динамически через {{ request.scheme }}://{{ request.get_host() }}
   - description: "Professional websites for local contractors"
   - telephone: "+1-555-123-4567"
   - email: "hello@contractorweb.dev"
   - address: PostalAddress (Austin, TX, US)
   - areaServed: "United States"

2. Обернуть в {% block structured_data %}...{% endblock %} чтобы дочерние
   шаблоны могли заменять или дополнять schema на конкретных страницах

Синтаксис — Jinja2. Кавычки внутри JSON экранировать правильно.

Файлы для изменения:
- templates/base.html (перед строкой {% block extra_js %})
```

---

## 🟡 PRIORITY 2 — Важные улучшения

---

### PROMPT-P2-1: SEO мета-теги для блога (base_blog.html + detail.html)

```
Добавь SEO мета-теги в шаблоны блога ContractorWeb.

Файлы:
- templates/blog/base_blog.html (базовый шаблон блога, строки 6-10)
- templates/blog/detail.html (шаблон статьи, строки 1-4)

Оба файла используют Jinja2.

Задача 1 — в base_blog.html после строки 7 (после meta description) добавить:
- <link rel="canonical"> с Jinja2-блоком canonical
- og:title, og:description, og:type="article", og:url, og:image (с блоками)
- twitter:card="summary_large_image", twitter:title, twitter:image (с блоками)
- Default og:image → /static/img/og-blog.png

Задача 2 — в detail.html после строки 4 ({% block meta_description %}) добавить
переопределение блоков из base_blog.html:
- {% block canonical %} → абсолютный URL статьи через request.build_absolute_uri()
- {% block og_title %} → {{ article.title }} | ContractorWeb Blog
- {% block og_description %} → {{ article.excerpt }}
- {% block og_image %} → {{ article.cover_image_url }} (если есть, иначе default)
- {% block twitter_image %} → аналогично og_image

Задача 3 — в detail.html в блок {% block extra_head %} добавить JSON-LD Article:
- @type: "Article"
- headline: article.title
- description: article.excerpt
- datePublished: article.published_at (ISO формат через .isoformat())
- dateModified: article.published_at
- image: article.cover_image_url
- publisher: Organization (ContractorWeb, logo URL)
- mainEntityOfPage: текущий URL статьи

Файлы для изменения:
- templates/blog/base_blog.html
- templates/blog/detail.html
```

---

### PROMPT-P2-2: Перенести img-comparison-slider в portfolio, Leaflet в service_area

```
Оптимизируй загрузку JS/CSS библиотек в проекте ContractorWeb.

Проблема: img-comparison-slider и Leaflet грузятся на ВСЕХ страницах через base.html,
хотя нужны только на конкретных страницах.

Шаг 1 — в templates/base.html:
- Найди строку 27: <link rel="stylesheet" href="https://unpkg.com/img-comparison-slider@8/dist/styles.css" />
  УДАЛИ её.
- Найди строку 154: <script type="module" src="https://unpkg.com/img-comparison-slider@8/dist/index.js"></script>
  УДАЛИ её.
- Найди подключение Leaflet CSS (ищи leaflet в base.html или service_area/index.html)
  Если Leaflet подключён в base.html — УДАЛИ оттуда.

Шаг 2 — в templates/portfolio/index.html:
- В блок {% block extra_head %} добавить:
  <link rel="stylesheet" href="https://unpkg.com/img-comparison-slider@8/dist/styles.css">
- В блок {% block extra_js %} добавить:
  <script type="module" src="https://unpkg.com/img-comparison-slider@8/dist/index.js"></script>

Шаг 3 — в templates/service_area/index.html:
- В блок {% block extra_head %} добавить Leaflet CSS (версия 1.9.x с unpkg CDN)
- В блок {% block extra_js %} добавить Leaflet JS (перед существующим кодом карты)

Важно: убедись что блоки extra_head и extra_js уже существуют в шаблонах.
Если нет — добавь их (они наследуются от base.html).

Файлы для изменения:
- templates/base.html (удаление строк)
- templates/portfolio/index.html (добавление в extra_head и extra_js)
- templates/service_area/index.html (добавление в extra_head и extra_js)
```

---

### PROMPT-P2-3: Добавить breadcrumbs на demo-страницы

```
Добавь навигационные хлебные крошки (breadcrumbs) на все demo-страницы ContractorWeb.

Страницы для изменения:
- templates/quote/index.html → Home / Demo Hub / Quote Calculator
- templates/emergency/index.html → Home / Demo Hub / Emergency Service
- templates/service_area/index.html → Home / Demo Hub / Service Area Map
- templates/portfolio/index.html → Home / Demo Hub / Portfolio
- templates/booking/index.html → Home / Demo Hub / Online Booking

Требования к разметке:
1. HTML: <nav aria-label="Breadcrumb"> → <ol> → <li> структура
2. Schema.org microdata: itemscope itemtype="https://schema.org/BreadcrumbList"
   на <ol>, каждый <li> с itemprop="itemListElement" и Schema.org ListItem
3. Стили: Tailwind CSS, текст серый, маленький, с разделителем "/"
4. Позиция: в начале блока {% block content %}, после открывающего контейнера div

Шаблон breadcrumb (Jinja2):
```html
<nav aria-label="Breadcrumb" class="max-w-5xl mx-auto px-4 pt-4">
  <ol class="flex items-center gap-1.5 text-xs text-gray-400"
      itemscope itemtype="https://schema.org/BreadcrumbList">
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a href="/" itemprop="item" class="hover:text-gray-600 transition-colors">
        <span itemprop="name">Home</span>
      </a>
      <meta itemprop="position" content="1">
    </li>
    <li aria-hidden="true" class="text-gray-300">/</li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a href="/demo/" itemprop="item" class="hover:text-gray-600 transition-colors">
        <span itemprop="name">Demo Hub</span>
      </a>
      <meta itemprop="position" content="2">
    </li>
    <li aria-hidden="true" class="text-gray-300">/</li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <span itemprop="name" class="text-gray-600">[НАЗВАНИЕ СТРАНИЦЫ]</span>
      <meta itemprop="position" content="3">
    </li>
  </ol>
</nav>
```

Последний элемент (текущая страница) — без ссылки, просто текст.

Файлы для изменения:
- templates/quote/index.html
- templates/emergency/index.html
- templates/service_area/index.html
- templates/portfolio/index.html
- templates/booking/index.html
```

---

### PROMPT-P2-4: Добавить H2-заголовки на лендинг

```
Добавь H2-заголовки в секции лендинга templates/landing/index.html.

Контекст:
- Файл: templates/landing/index.html
- НЕ наследует base.html — отдельный standalone HTML
- Правило проекта: НЕ менять визуальный дизайн, только добавлять H2 в правильные места
- Тайлвинд CSS уже подключён

Задача:
Найди в файле якорные секции и добавь H2 внутрь каждой секции:

1. Секция #features — добавить H2 в начало секции:
   <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 text-center mb-4">
     Website Features That Bring More Jobs
   </h2>

2. Секция #portfolio — добавить H2:
   <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 text-center mb-4">
     Websites We've Built for Contractors
   </h2>

3. Секция #pricing — добавить H2:
   <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 text-center mb-4">
     Simple, Transparent Pricing
   </h2>

4. Секция #contact — добавить H2:
   <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 text-center mb-4">
     Get Your Contractor Website Today
   </h2>

Если в секциях уже есть крупный текст (div с text-3xl и т.д.) — сделай его H2
вместо div, сохранив все классы. Не добавлять дублирующих заголовков.

Файлы для изменения:
- templates/landing/index.html
```

---

### PROMPT-P2-5: Добавить loading="lazy" и размеры к изображениям блога

```
Исправь теги изображений в шаблоне статьи блога ContractorWeb.

Файл: templates/blog/detail.html

Задача 1 — строка 70-72 (обложка статьи):
Текущий код:
  <img src="{{ article.cover_image_url }}"
       alt="{{ article.title }}"
       class="w-full h-full object-cover">

Заменить на:
  <img src="{{ article.cover_image_url }}"
       alt="{{ article.title }}"
       class="w-full h-full object-cover"
       loading="lazy"
       width="800"
       height="400">

Задача 2 — добавить контейнеру обложки (div выше img) атрибут style с aspect-ratio
чтобы предотвратить CLS до загрузки изображения:
  style="aspect-ratio: 2/1;"

или задать min-height: 200px через Tailwind: class добавить min-h-[200px]

Файлы для изменения:
- templates/blog/detail.html (строки ~68-74)
```

---

### PROMPT-P2-6: Создать кастомную 404 страницу

```
Создай кастомную страницу ошибки 404 для проекта ContractorWeb.

Контекст:
- Django 4.2 + Jinja2
- Кастомные error-шаблоны в Django с Jinja2 должны быть в templates/
  с именами 404.html и 500.html (Django ищет их автоматически при DEBUG=False)
- Шаблон должен использовать base.html через {% extends 'base.html' %}

Задача 1 — создать templates/404.html:
- Наследовать base.html
- Заполнить {% block title %}: "Page Not Found | ContractorWeb Demo"
- В {% block content %}:
  - Центрированный блок с большим "404"
  - Заголовок H1: "Page Not Found"
  - Подзаголовок: краткое объяснение
  - Кнопка "Go to Demo Hub" → /demo/
  - Кнопка "Go Home" → /
- Стили: Tailwind CSS, минимально, без лишнего

Задача 2 — создать templates/500.html (аналогично):
- Title: "Server Error | ContractorWeb Demo"
- H1: "Something Went Wrong"
- Кнопка "Go Home" → /

Задача 3 — в config/urls.py добавить:
  handler404 = 'django.views.defaults.page_not_found'
  handler500 = 'django.views.defaults.server_error'
(или кастомные view если нужна логика)

Примечание: 404.html должен работать БЕЗ context_processors если base.html
использует request.path — проверь что шаблон не падает при отсутствии request.

Файлы для создания/изменения:
- создать: templates/404.html
- создать: templates/500.html
- изменить: config/urls.py
```

---

### PROMPT-P2-7: Заменить inline SVG favicon на PNG файлы

```
Замени inline SVG favicon на стандартные PNG-файлы в проекте ContractorWeb.

Контекст:
- Текущий код в templates/base.html строка 16:
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔧</text></svg>">
- Папка для иконок: static/img/ (создать подпапку favicons/)

Задача 1 — создай SVG-файл `static/img/favicons/favicon.svg`:
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <text y=".9em" font-size="90">🔧</text>
  </svg>

Задача 2 — замени строку 16 в templates/base.html на:
  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="{{ static('img/favicons/favicon.svg') }}">
  <link rel="icon" type="image/png" sizes="32x32" href="{{ static('img/favicons/favicon-32.png') }}">
  <link rel="icon" type="image/png" sizes="16x16" href="{{ static('img/favicons/favicon-16.png') }}">
  <link rel="apple-touch-icon" sizes="180x180" href="{{ static('img/favicons/apple-touch-icon.png') }}">
  <meta name="theme-color" content="#1e3a5f">

Задача 3 — добавь в README или CLAUDE.md примечание:
  "Создать favicon-32.png, favicon-16.png, apple-touch-icon.png (180x180) в static/img/favicons/
   Можно сгенерировать на https://realfavicongenerator.net из SVG"

Задача 4 — создай placeholder-файлы (пустые PNG или скопируй из существующих):
  Если нет реальных PNG, оставь только SVG favicon и закомментируй PNG-строки,
  добавив TODO-комментарий.

Файлы для изменения:
- templates/base.html (строка 16)
- создать: static/img/favicons/favicon.svg
```

---

## 🟢 PRIORITY 3 — Рекомендации

---

### PROMPT-P3-1: Добавить meta robots с блоком в base.html

```
Добавь <meta name="robots"> тег в templates/base.html с возможностью
переопределения в дочерних шаблонах.

Контекст:
- base.html строка 5: <meta name="viewport" content="width=device-width, initial-scale=1.0">
- Demo-страницы — демонстрационные, их индексация обсуждаема
- Сейчас нет ни одного robots мета-тега

Задача — добавить после строки 5 (после viewport):
  <meta name="robots" content="{% block robots %}index, follow{% endblock %}">

Это позволит в любом дочернем шаблоне написать:
  {% block robots %}noindex, follow{% endblock %}

Дополнительно — реши стратегию для demo-страниц.
Два варианта (выбери один исходя из цели):

Вариант A (demo-страницы ИНДЕКСИРУЮТСЯ — показываем функционал в Google):
  Не менять дочерние шаблоны, оставить index, follow везде.

Вариант B (demo-страницы НЕ индексируются — экономим crawl budget):
  В templates/quote/index.html, emergency/index.html, service_area/index.html,
  portfolio/index.html, booking/index.html добавить в начало:
    {% block robots %}noindex, follow{% endblock %}

Файлы для изменения:
- templates/base.html (строка 6, после viewport)
- опционально: все demo-шаблоны (зависит от выбранного варианта)
```

---

### PROMPT-P3-2: Добавить dns-prefetch для Google Fonts

```
Оптимизируй загрузку Google Fonts в templates/base.html проекта ContractorWeb.

Контекст:
- Текущий код base.html строки 19-21:
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

Задача — заменить строки 19-21 на улучшенный вариант:
  <!-- DNS prefetch как fallback для старых браузеров -->
  <link rel="dns-prefetch" href="https://fonts.googleapis.com">
  <link rel="dns-prefetch" href="https://fonts.gstatic.com">
  <!-- Preconnect для современных браузеров -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <!-- Font с display=swap (уже есть, оставить) -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
        rel="stylesheet"
        media="print"
        onload="this.media='all'">
  <noscript>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  </noscript>

Объяснение media="print" trick:
  Браузер не блокирует рендеринг для print CSS. После загрузки onload меняет
  media="all". noscript — fallback для пользователей без JS.

Файлы для изменения:
- templates/base.html (строки 19-21)
```

---

### PROMPT-P3-3: Добавить aria-hidden к декоративным emoji

```
Добавь aria-hidden="true" ко всем декоративным emoji в шаблонах ContractorWeb.

Проблема: скринридеры зачитывают emoji как текст ("wrench", "lightning bolt"),
что ухудшает accessibility и косвенно влияет на SEO.

Найди и исправь во всех файлах шаблонов:

Правило: если emoji стоит рядом с текстом и является декоративным (не несёт
уникальной смысловой нагрузки) — добавить aria-hidden="true":
  <span aria-hidden="true">💰</span>

Если emoji — единственный контент элемента (нет текста рядом) — добавить role и aria-label:
  <span role="img" aria-label="Emergency alert icon">🚨</span>

Файлы для проверки и изменения:
- templates/demo_hub.html (feature-карточки с emoji-иконками)
- templates/quote/index.html (emoji в шагах формы)
- templates/emergency/index.html (emoji-бейджи доверия, шаги)
- templates/service_area/index.html (emoji в статистике)
- templates/booking/index.html (emoji в шагах)
- templates/base.html (emoji в demo-banner: ⚡)

Для каждого найденного emoji — определи контекст и добавь нужный атрибут.
Не менять визуальный вид, только добавлять атрибуты.
```

---

### PROMPT-P3-4: FAQ Schema на лендинг + rel="noreferrer" на внешние ссылки

```
Два небольших SEO-улучшения для проекта ContractorWeb.

=== Часть 1: FAQ Schema на лендинг ===

Файл: templates/landing/index.html

Задача: найди в файле секцию с FAQ или часто задаваемыми вопросами.
Если такой секции нет — добавить блок FAQ перед секцией #contact:

HTML:
<section class="py-16 bg-gray-50">
  <div class="max-w-3xl mx-auto px-4">
    <h2 class="text-2xl font-bold text-gray-900 text-center mb-8">
      Frequently Asked Questions
    </h2>
    <div class="space-y-4">
      <!-- 4-5 FAQ items в формате details/summary или accordion -->
    </div>
  </div>
</section>

JSON-LD (добавить перед </body> в landing/index.html):
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How long does it take to build a contractor website?",
      "acceptedAnswer": {"@type": "Answer", "text": "We deliver a complete contractor website within 5-7 business days after receiving your content and photos."}
    },
    {
      "@type": "Question",
      "name": "How much does a contractor website cost?",
      "acceptedAnswer": {"@type": "Answer", "text": "Our contractor websites start at a one-time fee. Check our pricing section for current packages."}
    },
    {
      "@type": "Question",
      "name": "Will my website work on mobile phones?",
      "acceptedAnswer": {"@type": "Answer", "text": "Yes, all our contractor websites are fully mobile-responsive and tested on phones and tablets."}
    }
  ]
}
</script>

=== Часть 2: rel="noopener noreferrer" ===

Файл: templates/booking/index.html

Найди: rel="noopener"
Замени на: rel="noopener noreferrer"

Файлы для изменения:
- templates/landing/index.html
- templates/booking/index.html
```

---

### PROMPT-P3-5: Security headers в production settings

```
Добавь security headers в production-настройки Django проекта ContractorWeb.

Контекст:
- Файл: config/settings/production.py
- Сайт будет деплоиться с HTTPS

Задача — добавить в config/settings/production.py следующие настройки:

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000        # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy — базовый
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True    # deprecated в Django 4.0+ но безвредно

Дополнительно — убедись что в MIDDLEWARE (в base.py или production.py) есть:
- 'django.middleware.security.SecurityMiddleware' — ПЕРВЫМ в списке
- 'django.middleware.clickjacking.XFrameOptionsMiddleware'

Файлы для изменения:
- config/settings/production.py
- проверить: config/settings/base.py (порядок MIDDLEWARE)
```

---

### PROMPT-P3-6: Добавить cross-linking между статьями блога

```
Добавь раздел "Related Articles" в конец страницы статьи блога ContractorWeb.

Контекст:
- Файл: templates/blog/detail.html
- Файл: apps/blog/views.py (нужно передать related_articles в контекст)
- Текущая структура detail.html строка 99-104:
  <hr class="my-10 border-gray-200">
  <a href="/blog/" ...>← Back to all articles</a>

Задача 1 — в apps/blog/views.py в view для detail-страницы добавить в context:
  'related_articles': Article.objects.filter(
      is_published=True
  ).exclude(id=article.id).order_by('-published_at')[:3]

Если в модели есть category — фильтровать по той же категории:
  'related_articles': Article.objects.filter(
      is_published=True,
      category=article.category
  ).exclude(id=article.id).order_by('-published_at')[:3]

Задача 2 — в templates/blog/detail.html перед тегом <hr> (строка ~99) добавить:
  {% if related_articles %}
  <section class="mt-12">
    <h2 class="text-xl font-bold text-gray-900 mb-6">Related Articles</h2>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {% for post in related_articles %}
      <a href="/blog/{{ post.slug }}/" class="block group rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
        {% if post.cover_image_url %}
        <img src="{{ post.cover_image_url }}" alt="{{ post.title }}"
             class="w-full h-32 object-cover" loading="lazy">
        {% endif %}
        <div class="p-3">
          <p class="text-sm font-semibold text-gray-900 group-hover:text-cyan-600 transition-colors line-clamp-2">
            {{ post.title }}
          </p>
        </div>
      </a>
      {% endfor %}
    </div>
  </section>
  {% endif %}

Сначала проверь реальные имена полей в модели Article (slug, title, cover_image_url,
is_published, published_at, category) — прочитай apps/blog/models.py перед изменениями.

Файлы для изменения:
- apps/blog/views.py (добавить related_articles в context)
- templates/blog/detail.html (добавить секцию Related Articles)
```

---

### PROMPT-P3-7: Добавить H3 для проектов в portfolio

```
Добавь H3-заголовки для каждого проекта в шаблоне portfolio ContractorWeb.

Контекст:
- Файл: templates/portfolio/index.html
- Проекты выводятся через {% for project in projects %}
- Каждый проект отображается через компонент <img-comparison-slider>
- Модель BeforeAfterProject имеет поля: title, category, description

Задача:
Найди в шаблоне цикл {% for project in projects %}.
Внутри каждой карточки проекта добавь H3 с названием проекта.

Если карточка проекта имеет примерную структуру:
  <div class="project-card ...">
    <img-comparison-slider>
      <img slot="first" ...>
      <img slot="second" ...>
    </img-comparison-slider>
    <!-- здесь нет заголовка -->
  </div>

Добавить ПОСЛЕ тега </img-comparison-slider>:
  <h3 class="text-sm font-semibold text-gray-800 mt-2 px-1">
    {{ project.title }}
  </h3>
  {% if project.category %}
  <p class="text-xs text-gray-500 px-1 mb-1">{{ project.category }}</p>
  {% endif %}

Прочитай templates/portfolio/index.html перед изменением чтобы вставить в правильное место.

Файлы для изменения:
- templates/portfolio/index.html
```

---

## 🗂️ Порядок выполнения промптов

```
НЕДЕЛЯ 1 (Критические):
  День 1: PROMPT-P1-1 (robots.txt) + PROMPT-P1-2 (sitemap.xml)
  День 2: PROMPT-P1-3 (canonical) + PROMPT-P1-5 (og:image, og:url)
  День 3: PROMPT-P1-4 (лендинг мета-теги)
  День 4: PROMPT-P1-6 (JSON-LD Organization schema)

НЕДЕЛЯ 2 (Важные):
  День 1: PROMPT-P2-2 (Leaflet + slider → страничная загрузка)
  День 2: PROMPT-P2-1 (блог мета-теги + Article schema)
  День 3: PROMPT-P2-3 (breadcrumbs)
  День 4: PROMPT-P2-4 (H2 на лендинге) + PROMPT-P2-5 (lazy img в блоге)
  День 5: PROMPT-P2-6 (404 страница) + PROMPT-P2-7 (favicon)

НЕДЕЛЯ 3 (Рекомендации):
  PROMPT-P3-1, P3-2, P3-3, P3-4, P3-5, P3-6, P3-7 — в любом порядке
```

---

*Каждый промпт проверен на соответствие ограничениям проекта:*
*Jinja2-синтаксис (не Django templates), не трогать landing app без явного указания,*
*мобильная совместимость, без npm/build step.*
