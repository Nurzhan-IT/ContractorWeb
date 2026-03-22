# Деплой ContractorWebDev на Ubuntu VPS

**Стек:** Django 5 · Gunicorn · Nginx · PostgreSQL · Cloudflare
**Домен:** contractorwebdev.com (DNS на Cloudflare)
**Сервер:** Ubuntu 22.04+ VPS (Vultr / DigitalOcean / Hetzner)

---

## Структура директорий на сервере

```
/var/www/contractorwebdev/
├── .env                        # секреты (chmod 600)
├── venv/                       # Python virtual environment
└── website_django/             # код проекта (git clone сюда)
    ├── deploy/
    │   ├── deploy.sh           # скрипт обновления
    │   ├── gunicorn.conf.py    # конфиг gunicorn
    │   ├── nginx.conf          # конфиг nginx
    │   └── contractorwebdev.service  # systemd unit
    ├── staticfiles/            # собирается через collectstatic
    └── media/                  # загружаемые файлы (portfolio images)
```

---

## Шаг 1. Системные пакеты

```bash
apt update && apt upgrade -y

apt install -y \
    python3.12 python3.12-venv python3-pip \
    nginx \
    postgresql postgresql-contrib \
    git \
    libpq-dev \
    libmagic1 \
    certbot
```

---

## Шаг 2. PostgreSQL — база данных

```bash
# Запустить и включить автозапуск
systemctl enable --now postgresql

# Создать пользователя и базу
sudo -u postgres psql <<'SQL'
CREATE USER contractorwebdev WITH PASSWORD 'STRONG_PASSWORD_HERE';
CREATE DATABASE contractorwebdev OWNER contractorwebdev;
GRANT ALL PRIVILEGES ON DATABASE contractorwebdev TO contractorwebdev;
SQL
```

> Пароль запомни — он пойдёт в `DATABASE_URL` в `.env`.

---

## Шаг 3. Системный пользователь и директории

```bash
# Создать пользователя без login shell
useradd --system --no-create-home --shell /usr/sbin/nologin contractorwebdev

# Создать структуру директорий
mkdir -p /var/www/contractorwebdev
chown contractorwebdev:contractorwebdev /var/www/contractorwebdev
```

---

## Шаг 4. Клонировать репозиторий

```bash
cd /var/www/contractorwebdev

git clone https://github.com/YOUR_USERNAME/website_django.git website_django

# Разрешить git для root (если запускаешь как root)
git config --global --add safe.directory /var/www/contractorwebdev/website_django
```

---

## Шаг 5. Python virtual environment и зависимости

```bash
cd /var/www/contractorwebdev

# Создать venv
python3.12 -m venv venv

# Установить зависимости
venv/bin/pip install --upgrade pip
venv/bin/pip install -r website_django/requirements.txt
```

---

## Шаг 6. Файл .env

```bash
# Создать файл
nano /var/www/contractorwebdev/.env
```

Содержимое (пример в `deploy/env.production.example`):

```env
DJANGO_SETTINGS_MODULE=config.settings.production

# Сгенерировать: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=your-very-long-random-secret-key

# PostgreSQL
DATABASE_URL=postgresql://contractorwebdev:STRONG_PASSWORD_HERE@localhost:5432/contractorwebdev?sslmode=prefer

# Домены через запятую, без пробелов
ALLOWED_HOSTS=contractorwebdev.com,www.contractorwebdev.com

# OpenRouter AI (для Quote Calculator)
OPENROUTER_API_KEY=sk-or-v1-...

# Cloudflare Turnstile (captcha)
CF_TURNSTILE_SITE_KEY=0x4AAAA...
CF_TURNSTILE_SECRET_KEY=0x4AAAA...

# Cal.com (для Booking)
CAL_API_KEY=cal_live_...
CAL_USERNAME=your-cal-username
CAL_SLUG_PLUMBING=plumbing-repair
CAL_SLUG_FAUCET=faucet-toilet
CAL_SLUG_ELECTRICAL=electrical-work
```

```bash
# Закрыть доступ к файлу с секретами
chmod 600 /var/www/contractorwebdev/.env
chown contractorwebdev:contractorwebdev /var/www/contractorwebdev/.env
```

> **Важно:** `SECRET_KEY` часто содержит спецсимволы (`^`, `#`, `%`).
> Не используй `source .env` в bash — он сломается. `production.py` загружает
> `.env` автоматически через `python-dotenv`, никаких дополнительных действий не нужно.

---

## Шаг 7. Django — первичная настройка

```bash
cd /var/www/contractorwebdev/website_django

# Все manage.py команды запускаются так:
DJANGO_SETTINGS_MODULE=config.settings.production \
    /var/www/contractorwebdev/venv/bin/python manage.py collectstatic --noinput

DJANGO_SETTINGS_MODULE=config.settings.production \
    /var/www/contractorwebdev/venv/bin/python manage.py migrate --noinput

# Загрузить тестовые данные портфолио
DJANGO_SETTINGS_MODULE=config.settings.production \
    /var/www/contractorwebdev/venv/bin/python manage.py loaddata portfolio

# Создать admin пользователя
DJANGO_SETTINGS_MODULE=config.settings.production \
    /var/www/contractorwebdev/venv/bin/python manage.py createsuperuser
```

```bash
# Выставить права на папки
chown -R contractorwebdev:contractorwebdev /var/www/contractorwebdev/website_django/staticfiles
chown -R contractorwebdev:contractorwebdev /var/www/contractorwebdev/website_django/media
```

---

## Шаг 8. SSL — Cloudflare Origin Certificate

В Cloudflare Dashboard:
`SSL/TLS → Origin Server → Create Certificate → выбрать домены → Create`

Скачать два файла и положить на сервер:

```bash
mkdir -p /etc/ssl/cloudflare

# Вставить содержимое сертификата (вкладка "Origin Certificate")
nano /etc/ssl/cloudflare/contractorwebdev.pem

# Вставить содержимое приватного ключа
nano /etc/ssl/cloudflare/contractorwebdev.key

chmod 600 /etc/ssl/cloudflare/contractorwebdev.key
chmod 644 /etc/ssl/cloudflare/contractorwebdev.pem
```

В Cloudflare: `SSL/TLS → Overview → режим Full (strict)`

---

## Шаг 9. Nginx

```bash
# Скопировать конфиг
cp /var/www/contractorwebdev/website_django/deploy/nginx.conf \
   /etc/nginx/sites-available/contractorwebdev

# Активировать
ln -s /etc/nginx/sites-available/contractorwebdev \
      /etc/nginx/sites-enabled/contractorwebdev

# Убрать дефолтный сайт (если мешает)
rm -f /etc/nginx/sites-enabled/default

# Проверить конфиг и перезапустить
nginx -t
systemctl enable --now nginx
```

---

## Шаг 10. Systemd сервис (Gunicorn)

```bash
# Скопировать unit файл
cp /var/www/contractorwebdev/website_django/deploy/contractorwebdev.service \
   /etc/systemd/system/contractorwebdev.service

# Перечитать конфиги и запустить
systemctl daemon-reload
systemctl enable --now contractorwebdev
```

---

## Шаг 11. Firewall

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

---

## Шаг 12. Проверка работоспособности

```bash
# Все сервисы запущены?
systemctl status contractorwebdev nginx postgresql

# Сокет gunicorn существует?
ls -la /run/contractorwebdev/gunicorn.sock

# Конфиг nginx валиден?
nginx -t

# Порты 80/443 слушают?
ss -tlnp | grep -E '80|443'

# Сайт отвечает снаружи (должен вернуть HTTP/2 200)
curl -I https://contractorwebdev.com

# Логи gunicorn
journalctl -u contractorwebdev -n 50 --no-pager

# Логи nginx
tail -30 /var/log/nginx/contractorwebdev_error.log
```

> **Норма:** `curl` напрямую через сокет вернёт `400 Bad Request` — это ожидаемо,
> потому что `Host: localhost` не в `ALLOWED_HOSTS`. Через Cloudflare всё работает.

---

## Шаг 13. Cron — очистка старых запросов (GDPR)

```bash
crontab -e -u contractorwebdev
```

Добавить одну строку (без переносов `\`):

```
0 3 * * * DJANGO_SETTINGS_MODULE=config.settings.production /var/www/contractorwebdev/venv/bin/python /var/www/contractorwebdev/website_django/manage.py cleanup_old_quotes --days=90
```

Проверить:

```bash
crontab -l -u contractorwebdev
```

---

## Обновление сайта (после git push)

```bash
# Сделать deploy.sh исполняемым (один раз)
chmod +x /var/www/contractorwebdev/website_django/deploy/deploy.sh

# Каждое обновление:
sudo /var/www/contractorwebdev/website_django/deploy/deploy.sh
```

Скрипт автоматически: `git pull` → `pip install` → `collectstatic` → `migrate` → `reload gunicorn`

---

## Команды для обслуживания

```bash
# Перезапустить приложение (с даунтаймом)
systemctl restart contractorwebdev

# Перезагрузить без даунтайма (после изменений кода)
systemctl reload contractorwebdev

# Посмотреть живые логи
journalctl -u contractorwebdev -f

# Django shell в production
DJANGO_SETTINGS_MODULE=config.settings.production \
    /var/www/contractorwebdev/venv/bin/python \
    /var/www/contractorwebdev/website_django/manage.py shell

# Бекап базы данных
sudo -u postgres pg_dump contractorwebdev > backup_$(date +%Y%m%d).sql
```

---

## Конфиг Gunicorn (deploy/gunicorn.conf.py)

| Параметр | Значение | Описание |
|----------|----------|----------|
| `worker_class` | `gthread` | Потоки вместо блокирующего sync |
| `workers` | `cpu_count × 2 + 1` | Авто по ядрам (1 vCPU → 3 воркера) |
| `threads` | `4` | Потоков на воркер → 12 concurrent |
| `timeout` | `120s` | Для медленных AI запросов |
| `preload_app` | `True` | Быстрый старт воркеров, меньше RAM |

---

## Возможные проблемы

### `SECRET_KEY` ломает `source .env`
Спецсимволы (`^`, `#`, `%`, `@`) интерпретируются bash как команды.
**Решение:** не нужно sourcing — `production.py` сам загружает `.env` через python-dotenv.

### `collectstatic` падает с `ImproperlyConfigured: STATIC_ROOT`
Значит Django использует `local.py` вместо `production.py`.
**Решение:** явно указывать `DJANGO_SETTINGS_MODULE=config.settings.production`.

### `git pull` ошибка `detected dubious ownership`
Git видит что репозиторий принадлежит другому пользователю.
**Решение:** `git config --global --add safe.directory /var/www/contractorwebdev/website_django`

### Crontab: `bad minute` ошибка
В crontab нельзя переносить команду на новую строку через `\`.
**Решение:** вся команда cron — одна строка без переносов.

### `curl` через сокет возвращает `400`
Ожидаемо: `Host: localhost` не в `ALLOWED_HOSTS`. Через nginx/Cloudflare работает нормально.
