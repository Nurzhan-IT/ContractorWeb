# SEO Prompts — Исправления в коде

Каждый промпт независим. Выполнять по порядку — каждый следующий может зависеть от изменений предыдущего.

---

## Промпт 1 — Починить robots.txt

```
В файле templates/robots.txt строка:

    Sitemap: https://{{ site_domain }}/sitemap.xml

рендерится пустой — переменная site_domain никуда не передаётся.
Роут зарегистрирован в config/urls.py через TemplateView без extra_context.

Замени {{ site_domain }} на захардкоженный домен. Итоговая строка:

    Sitemap: https://contractorwebdev.com/sitemap.xml

Также добавь Disallow на /demo/ и /contact/ — эти страницы не нужно
индексировать:

    Disallow: /admin/
    Disallow: /api/
    Disallow: /demo/
    Disallow: /contact/

Больше ничего не меняй.
```

---

## Промпт 2 — Добавить поле updated_at в модель Article

```
В apps/blog/models.py модель Article не отслеживает дату последнего изменения.
Это поле нужно для корректного lastmod в sitemap.xml и dateModified в JSON-LD схеме.

Добавь в класс Article одно поле после is_published:

    updated_at = models.DateTimeField(auto_now=True)

После изменения модели создай и примени миграцию:

    python manage.py makemigrations blog
    python manage.py migrate

Больше ничего не меняй.
```

---

## Промпт 3 — Обновить sitemap: блог и удалить /demo/

```
Файл config/sitemaps.py и config/urls.py содержат sitemap-конфиг.

Задача 1 — BlogSitemap.lastmod должен отдавать дату последнего изменения,
а не дату публикации. После того как в модель Article добавлено поле updated_at,
измени метод lastmod:

    def lastmod(self, obj):
        return obj.updated_at

Задача 2 — Удали DemoSitemap из sitemaps.py полностью (класс и импорт).
Демо-страницы /demo/* не должны индексироваться.

Задача 3 — В config/urls.py убери 'demo' из словаря sitemaps:

    sitemaps = {
        'landing': LandingSitemap,
        'services': ServicePagesSitemap,
        'blog_index': BlogIndexSitemap,
        'blog': BlogSitemap,
    }

Больше ничего не меняй.
```

---

## Промпт 4 — Скрыть служебные роуты от индексации (noindex)

```
Демо-страницы /demo/* и юридические страницы /privacy/, /terms/, /cookies/
не должны индексироваться Google. Вместо запрета в robots.txt используем
meta robots noindex прямо в шаблонах — это более надёжный способ.

Шаг 1 — Найди базовый шаблон демо-страниц. По структуре проекта это base.html
(или отдельный базовый шаблон для /demo/*). Проверь какой шаблон extend'ят
templates/demo_hub.html, templates/quote/index.html, templates/emergency/index.html,
templates/service_area/index.html, templates/portfolio/index.html,
templates/booking/index.html.

Шаг 2 — В блоке {% block extra_head %} каждого из этих шаблонов добавь:

    <meta name="robots" content="noindex, follow">

Добавь этот тег в сами page-шаблоны (не в базовый), чтобы не затронуть
другие страницы использующие тот же base.

Шаг 3 — Добавь <meta name="robots" content="noindex, follow"> в:
- templates/legal/privacy.html
- templates/legal/terms.html
- templates/legal/cookies.html

Шаг 4 — Убедись, что в base_landing.html и base_landing_solid_navbar.html
блок meta robots НЕ содержит noindex (там должен быть index, follow).

Больше ничего не меняй.
```

---

## Промпт 5 — Улучшить Open Graph и JSON-LD для статей блога

```
Файл templates/blog/detail.html содержит мета-теги и JSON-LD схему.

Задача 1 — Добавь article: Open Graph мета-теги и явный og:type в {% block extra_head %}
ДО тега <script type="application/ld+json">:

    <meta property="og:type" content="article">
    <meta property="article:published_time" content="{{ article.published_at.isoformat() }}">
    <meta property="article:modified_time" content="{{ article.updated_at.isoformat() }}">
    {% if article.category %}
    <meta property="article:section" content="{{ article.category.name }}">
    {% endif %}

Задача 2 — В JSON-LD схеме Article исправь dateModified чтобы использовал updated_at:

    "dateModified": "{{ article.updated_at.isoformat() }}",

Больше ничего не меняй.
```

---

## Промпт 6 — Добавить BreadcrumbList и CollectionPage на страницу блога

```
Файл templates/blog/index.html — страница листинга блога. На ней отсутствует
JSON-LD разметка, которую Google использует для отображения breadcrumbs
в результатах поиска.

Найди в шаблоне блок {% block extra_head %} (или создай его если его нет,
перед закрывающим </head>) и добавь два JSON-LD объекта:

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://contractorwebdev.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Blog",
      "item": "https://contractorwebdev.com/blog/"
    }
  ]
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Contractor Website Tips & SEO Blog",
  "description": "Articles about contractor websites, local SEO, online booking, and lead generation for plumbers, electricians, and roofers.",
  "url": "https://contractorwebdev.com/blog/",
  "publisher": {
    "@type": "Organization",
    "name": "ContractorWebDev",
    "url": "https://contractorwebdev.com/"
  }
}
</script>

Больше ничего не меняй.
```

---

## Промпт 7 — Google Analytics 4 через переменную окружения

```
Нужно подключить Google Analytics 4 к сайту. Measurement ID должен
храниться в .env, а не хардкодиться в шаблонах.

Шаг 1 — В config/settings/base.py добавь:

    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')

Убедись что import os есть в начале файла.

Шаг 2 — Найди context processor для шаблонов или создай новый файл
config/context_processors.py:

    from django.conf import settings

    def analytics(request):
        return {
            'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        }

Шаг 3 — Добавь этот context processor в TEMPLATES в base.py.
Найди секцию 'context_processors' в бэкенде Jinja2 (django_jinja или аналог)
и добавь 'config.context_processors.analytics'.

Шаг 4 — В templates/base_landing.html и templates/base_landing_solid_navbar.html
добавь перед закрывающим </head>:

    {% if GOOGLE_ANALYTICS_ID %}
    <script async src="https://www.googletagmanager.com/gtag/js?id={{ GOOGLE_ANALYTICS_ID }}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '{{ GOOGLE_ANALYTICS_ID }}');
    </script>
    {% endif %}

Шаг 5 — Добавь в .env.example:

    # Google Analytics 4
    GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX

Шаг 6 — Добавь в .env (реальный файл) свой Measurement ID из Google Analytics.

Больше ничего не меняй.
```

---

## Порядок выполнения

| # | Промпт | Зависимости | Риск |
|---|---|---|---|
| 1 | robots.txt | — | Низкий |
| 2 | Article model + миграция | — | Средний (миграция БД) |
| 3 | Sitemap обновление | Промпт 2 (нужен updated_at) | Низкий |
| 4 | Noindex на служебные страницы | — | Низкий |
| 5 | OG + JSON-LD для статей | Промпт 2 (нужен updated_at, seo_title и т.д.) | Низкий |
| 6 | BreadcrumbList на блог | — | Низкий |
| 7 | Google Analytics 4 | — | Низкий |
