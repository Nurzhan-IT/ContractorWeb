# ContractorWebDev

Django-проект веб-агентства, специализирующейся на сайтах для подрядчиков (сантехники,
электрики, кровельщики, HVAC). Совмещает маркетинговый сайт агентства, каталог
демо-фич для потенциальных клиентов и white-label лендинги под конкретные компании.

## Что внутри

**Маркетинговый сайт агентства**
- Лендинг с формой AI-квоута (оценка стоимости работ по описанию + фото)
- SEO-лендинги под услуги (дизайн сайтов, SEO, лидогенерация) для каждой ниши: сантехника,
  электрика, кровля, HVAC, генеральный подряд
- Блог с Markdown-контентом, категориями и админкой
- `sitemap.xml`, `robots.txt`, юридические страницы

**Демо-хаб** (`/demo/`) — витрина интерактивных фич, которые агентство продаёт клиентам:
- Калькулятор мгновенной оценки стоимости (AI, фото + описание проблемы → PDF-смета)
- Форма экстренного вызова 24/7 (симуляция SMS-уведомления и ETA)
- Карта зоны обслуживания (геокодинг ZIP-кода, проверка радиуса на Leaflet)
- Слайдер "до/после" по портфолио выполненных работ
- Онлайн-запись на визит через встроенный Cal.com

**White-label лендинги** (`/demo/plumbing/<slug>/`) — готовый шаблон сайта под конкретную
сантехническую компанию: своя AI-форма оценки, двуязычный интерфейс (en/es), генерация
PDF-сметы с логотипом клиента. Компании и их данные (включая массовый импорт через CSV)
управляются из Django admin.

## Стек

| Слой | Технология |
|---|---|
| Backend | Django 5.2 |
| Шаблоны | Jinja2 (django-jinja) |
| БД | SQLite (dev) / PostgreSQL (prod, docker) |
| AI | OpenRouter API (Gemini 2.5 Flash) |
| PDF | ReportLab |
| Геокодинг | geopy + Nominatim |
| Карта | Leaflet.js (CDN) |
| Онлайн-запись | Cal.com Embed |
| Слайдер "до/после" | img-comparison-slider (CDN) |
| Капча | Cloudflare Turnstile |
| Markdown → HTML | markdown + bleach |
| Стили | Tailwind CSS v3 (standalone CLI, без npm) |
| Контейнеризация | Docker, docker-compose, gunicorn + whitenoise |
| CI | GitHub Actions: тесты, ruff, `check --deploy`, сборка Tailwind, docker-test |

Никакого npm и фронтенд-сборки — все JS-библиотеки подключены через CDN. Исключение —
Tailwind, который компилируется отдельным CLI-бинарником.

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env          # задать SECRET_KEY и остальные переменные
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открыть [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Через Docker

```bash
cp .env.example .env
docker compose up --build
```

Поднимает приложение и PostgreSQL; миграции применяются автоматически при старте контейнера.

## Структура проекта

```
apps/
├── landing/     # главная страница агентства + форма контакта
├── web_quote/   # AI-форма оценки стоимости на лендинге
├── services/    # SEO-лендинги услуг (дизайн, SEO, лидогенерация по нишам)
├── blog/        # блог: категории, статьи в Markdown
├── plumbing/    # white-label сайты под конкретные сантехнические компании
├── demo/        # хаб демо-фич
├── quote/       # Feature: AI-калькулятор оценки стоимости
├── emergency/   # Feature: экстренный вызов (симуляция)
├── service_area/# Feature: карта зоны обслуживания
├── portfolio/   # Feature: галерея "до/после"
└── booking/     # Feature: онлайн-запись через Cal.com
config/
├── settings/    # local / docker / production
├── urls.py, demo_urls.py, api_urls.py, sitemaps.py
```

Подробное описание ответственности каждого приложения, API-эндпоинтов и правил проекта —
в [CLAUDE.md](CLAUDE.md).

## Переменные окружения

См. [.env.example](.env.example): ключ Django, строка подключения к БД, ключ OpenRouter
(AI-оценки), ключи Cloudflare Turnstile (капча), ключи Cal.com (онлайн-запись), ID Google
Analytics.

## Tailwind CSS

Собирается отдельным CLI-бинарником, без Node.js:

```powershell
.\build_tailwind.ps1
```

Запускать при добавлении новых Tailwind-классов в шаблоны или JS. Результат
(`static/css/tailwind.css`) коммитится в git — на сервере пересборка не нужна.

## Тесты

```bash
python manage.py test booking quote services
```

CI (GitHub Actions) на каждый push/PR в `main` прогоняет тесты, линтер ruff, проверку
`check --deploy`, сборку Tailwind-стадии Docker-образа и полный docker-compose тест-запуск.

## Деплой

Продакшн-настройки — `config/settings/production.py` (PostgreSQL, статика через
whitenoise, HTTPS/HSTS). Образ собирается многостадийным `Dockerfile` (venv → сборка
Tailwind → runtime), запускается через gunicorn под непривилегированным пользователем,
health-check — `/healthz/`.
