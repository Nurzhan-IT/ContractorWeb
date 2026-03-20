# Юридический аудит соответствия — ContractorPro Demo Site

> **Дата проверки:** 2026-03-19
> **Проверяемая система:** Django-сайт веб-агентства с демо-функциями для подрядчиков
> **Правовые зоны:** GDPR (ЕС), CCPA (Калифорния), FTC (США), EU AI Act, ADA/WCAG

---

## Резюме

Сайт собирает персональные данные через несколько форм и хранит их в двух моделях БД. Технические средства защиты (CSRF, rate limiting, отсутствие трекинга) на хорошем уровне. Однако **юридическая документация и механизмы согласия полностью отсутствуют**, что создаёт серьёзные правовые риски при работе с реальными пользователями.

---

## КРИТИЧЕСКИЕ НАРУШЕНИЯ ❌ — Обязательно исправить

---

### 1. Отсутствует Политика конфиденциальности

**Нарушает:** GDPR ст. 13/14, CCPA §1798.100, рекомендации FTC
**Риск:** Штраф по GDPR до €20 млн или 4% годового оборота; по CCPA $2 500–$7 500 за каждое нарушение

**Что собирается прямо сейчас без каких-либо уведомлений:**

| Форма | Файл модели | Данные |
|---|---|---|
| Quote Calculator | `apps/quote/models.py` | Имя, телефон, email, адрес, ZIP, IP, ответы ИИ |
| Web Quote (лендинг) | `apps/web_quote/models.py` | Имя, email, телефон, сфера, бюджет, сроки, IP, ответы ИИ |

Данные хранятся **бессрочно**, нет ни TTL, ни механизма удаления.

---

#### Варианты решения:

**Вариант А — Минимальный (быстрый старт, 1–2 часа)**
Создать статическую страницу `/privacy/` с базовым текстом на основе шаблона (Iubenda, Termly, PrivacyPolicies.com — бесплатные генераторы). Добавить маршрут в `config/urls.py` и ссылку в футер.

```python
# config/urls.py
from django.views.generic import TemplateView
urlpatterns += [
    path('privacy/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy'),
    path('terms/',   TemplateView.as_view(template_name='legal/terms.html'),   name='terms'),
    path('cookies/', TemplateView.as_view(template_name='legal/cookies.html'), name='cookies'),
]
```

**Вариант Б — Через Django-модель (рекомендуется, ~3 часа)**
Создать приложение `apps/legal/` с моделью `LegalDocument(slug, title, content_markdown, updated_at)`. Управлять контентом через Django Admin. Пользователь всегда видит актуальную версию.

```python
# apps/legal/models.py
class LegalDocument(models.Model):
    slug    = models.SlugField(unique=True)  # 'privacy', 'terms', 'cookies'
    title   = models.CharField(max_length=200)
    content = models.TextField()             # Markdown
    updated_at = models.DateTimeField(auto_now=True)
```

**Вариант В — Внешний сервис (0 часов разработки)**
Использовать Iubenda или Termly — они предоставляют готовый хостинг для политик, обновляются автоматически при изменении законодательства, интегрируются одним скриптом. Платные планы от $9/мес, есть бесплатные базовые.

---

### 2. Отсутствует баннер согласия на cookie

**Нарушает:** GDPR Recital 32, ePrivacy Directive (ЕС), PECR (Великобритания)
**Файл:** `config/middleware.py` — `EnsureCsrfCookieMiddleware` принудительно устанавливает `csrftoken` на каждый ответ **до получения согласия пользователя**. Django также устанавливает `sessionid`.

Согласно ePrivacy Directive, даже технически необходимые cookies должны быть **раскрыты** пользователю. Без уведомления сайт нарушает минимальные требования.

---

#### Варианты решения:

**Вариант А — DIY-баннер (1–2 часа, без зависимостей)**
Добавить баннер в `base.html`, сохранять согласие в `localStorage`. `csrftoken` и `sessionid` указать как «строго необходимые» (не требуют opt-in, но должны быть раскрыты).

```html
<!-- templates/base.html — добавить перед </body> -->
<div id="cookie-banner" class="fixed bottom-0 inset-x-0 bg-gray-900 text-white p-4 z-50 hidden">
  <div class="max-w-5xl mx-auto flex flex-col sm:flex-row items-center gap-4">
    <p class="text-sm">
      Мы используем необходимые cookie (CSRF-защита, сессия).
      <a href="/cookies/" class="underline">Подробнее</a>
    </p>
    <div class="flex gap-3 shrink-0">
      <button onclick="acceptCookies()" class="bg-blue-600 px-4 py-2 rounded text-sm">Принять</button>
      <a href="/cookies/" class="border border-white px-4 py-2 rounded text-sm">Настройки</a>
    </div>
  </div>
</div>
<script>
  function acceptCookies() {
    localStorage.setItem('cookie_consent', 'accepted');
    document.getElementById('cookie-banner').classList.add('hidden');
  }
  if (!localStorage.getItem('cookie_consent')) {
    document.getElementById('cookie-banner').classList.remove('hidden');
  }
</script>
```

**Вариант Б — Библиотека Cookie Consent by Osano (30 минут, бесплатно)**
Готовое решение с категориями, поддержкой GDPR и CCPA, адаптивным дизайном.

```html
<!-- base.html <head> -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/vanilla-cookieconsent@3/dist/cookieconsent.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/vanilla-cookieconsent@3/dist/cookieconsent.umd.js"></script>
<script>
  window.addEventListener('load', function() {
    CookieConsent.run({
      categories: {
        necessary: { enabled: true, readOnly: true }
      },
      language: {
        default: 'ru',
        translations: {
          ru: {
            consentModal: {
              title: 'Мы используем cookie',
              description: 'Только необходимые cookie для защиты форм (CSRF) и сессии.',
              acceptAllBtn: 'Принять',
              showPreferencesBtn: 'Подробнее'
            }
          }
        }
      }
    });
  });
</script>
```

**Вариант В — Iubenda / Termly (0 часов, SaaS)**
Те же сервисы, что для политики конфиденциальности — включают баннер cookie в свои планы. Управление осуществляется из личного кабинета без изменений в коде.

---

### 3. Отсутствуют Условия использования (Terms of Service)

**Нарушает:** Общие нормы защиты потребителей; создаёт риск ответственности за ИИ-оценки
**Особая опасность:** ИИ генерирует ценовые оценки — пользователь может принять их за профессиональное заключение, принять финансовое решение и потребовать компенсации.

---

#### Варианты решения:

**Вариант А — Статическая страница с ключевыми клаузулами (1 час)**
Обязательные разделы: ограничение ответственности за ИИ-оценки, демо-характер сервиса, возрастные ограничения, юрисдикция споров.

```html
<!-- templates/legal/terms.html — ключевой блок -->
<section>
  <h2>Ограничение ответственности за ИИ-оценки</h2>
  <p>
    Все ценовые оценки на данном сайте генерируются искусственным интеллектом
    (Google Gemini через OpenRouter) и носят исключительно ориентировочный характер.
    Они <strong>не являются профессиональной оценкой, коммерческим предложением
    или договором</strong>. Точная стоимость определяется только после выезда
    специалиста на объект.
  </p>
</section>
```

**Вариант Б — Онлайн-генератор (30 минут)**
Ресурсы: Termly.io, PrivacyPolicies.com, Rocket Lawyer. Заполнить форму — получить готовый текст. Разместить на `/terms/`.

**Вариант В — Юридическая консультация (рекомендуется для продакшена)**
Если сайт будет принимать реальные заявки от реальных клиентов — заказать документ у юриста ($200–$500). Особенно важно для клаузул об ИИ-ответственности в свете EU AI Act 2024.

---

### 4. Отсутствуют чекбоксы согласия на обработку данных в формах

**Нарушает:** GDPR ст. 7 (согласие должно быть «свободным, конкретным, информированным и однозначным»)
**Затронутые файлы:**
- `templates/quote/index.html` — Quote Calculator
- `templates/landing/index.html` — Web Quote форма лендинга

Cloudflare Turnstile присутствует, но это **защита от ботов**, а не согласие на обработку персональных данных — это разные вещи.

---

#### Варианты решения:

**Вариант А — Простой обязательный чекбокс (30 минут)**

```html
<!-- Добавить в каждую форму перед кнопкой отправки -->
<div class="flex items-start gap-3 mt-4">
  <input type="checkbox" id="consent" name="consent" required
         class="mt-1 h-4 w-4 rounded border-gray-300">
  <label for="consent" class="text-sm text-gray-600">
    Я принимаю
    <a href="/privacy/" class="text-blue-600 underline">Политику конфиденциальности</a>
    и соглашаюсь на обработку моих данных, включая передачу Google Gemini AI
    для генерации оценки.
  </label>
</div>
```

**Вариант Б — Двухуровневое согласие (60 минут, для GDPR)**
Разделить согласие на обязательное (обработка данных) и опциональное (маркетинг):

```html
<fieldset class="space-y-2 mt-4">
  <div class="flex items-start gap-3">
    <input type="checkbox" id="consent_required" name="consent_required" required class="mt-1">
    <label for="consent_required" class="text-sm">
      <strong>Обязательно:</strong> Я согласен на обработку персональных данных
      согласно <a href="/privacy/" class="underline">Политике конфиденциальности</a>
    </label>
  </div>
  <div class="flex items-start gap-3">
    <input type="checkbox" id="consent_marketing" name="consent_marketing" class="mt-1">
    <label for="consent_marketing" class="text-sm text-gray-500">
      <strong>Опционально:</strong> Я согласен получать информационные материалы
      об услугах агентства на указанный email
    </label>
  </div>
</fieldset>
```

**Вариант В — Валидация на бэкенде**
Помимо HTML-атрибута `required`, добавить проверку на сервере:

```python
# apps/quote/views.py — QuoteSubmitView
def post(self, request):
    consent = request.POST.get('consent')
    if not consent:
        return JsonResponse({'error': 'Необходимо согласие на обработку данных'}, status=400)
    # ... остальная логика
```

---

### 5. Отсутствует политика хранения данных и механизм удаления

**Нарушает:** GDPR ст. 5(1)(e) — принцип ограничения хранения; ст. 17 — право на удаление («право быть забытым»)

Записи в `QuoteRequest` и `WebQuoteRequest` хранятся **бессрочно**. Пользователь не может удалить свои данные.

---

#### Варианты решения:

**Вариант А — Команда управления для очистки (2 часа)**

```python
# apps/quote/management/commands/cleanup_old_quotes.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.quote.models import QuoteRequest
from apps.web_quote.models import WebQuoteRequest

class Command(BaseCommand):
    help = 'Удаляет записи старше 90 дней'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=90)
        deleted_q, _ = QuoteRequest.objects.filter(created_at__lt=cutoff).delete()
        deleted_wq, _ = WebQuoteRequest.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f'Удалено: {deleted_q} quote-запросов, {deleted_wq} web-quote-запросов')
```

Добавить в cron (Linux) или Windows Task Scheduler:
```bash
# Запуск ежедневно в 03:00
0 3 * * * cd /path/to/project && python manage.py cleanup_old_quotes
```

**Вариант Б — API-эндпоинт для удаления по запросу пользователя (3 часа)**

```python
# config/api_urls.py — добавить
path('data/delete/', DataDeleteView.as_view(), name='data-delete'),

# apps/landing/views.py — новый класс
class DataDeleteView(View):
    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        if not email:
            return JsonResponse({'error': 'Email обязателен'}, status=400)

        from apps.quote.models import QuoteRequest
        from apps.web_quote.models import WebQuoteRequest

        deleted_q = QuoteRequest.objects.filter(email__iexact=email).delete()[0]
        deleted_wq = WebQuoteRequest.objects.filter(email__iexact=email).delete()[0]

        return JsonResponse({
            'status': 'ok',
            'message': f'Удалено {deleted_q + deleted_wq} записей, связанных с {email}'
        })
```

**Вариант В — Автоматическое TTL через Django-lifecycle или celery-beat (4 часа)**
Если в проекте уже используется Celery, добавить периодическую задачу. Если нет — библиотека `django-lifecycle` позволяет настроить хуки на сигналы модели без Celery.

---

## ПРЕДУПРЕЖДЕНИЯ ⚠️ — Желательно исправить

---

### 6. Неполное раскрытие информации об ИИ-обработке

**Нарушает:** FTC Act §5 (США), EU AI Act ст. 50 (прозрачность), GDPR ст. 22 (автоматизированные решения)

**Проблема:**
- `templates/landing/index.html` — упоминает «Powered by Gemini AI» ✅
- `templates/quote/index.html` — говорит «AI-powered», но **не раскрывает**, что данные передаются OpenRouter → Google
- **Нигде не указано**, что загружаемые фото конвертируются в base64 и отправляются в стороннюю ИИ-систему (см. `apps/quote/ai_service.py`)

---

#### Варианты решения:

**Вариант А — Информационный блок над формой (30 минут)**

```html
<!-- templates/quote/index.html — добавить над формой -->
<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
  <p class="text-sm text-blue-800">
    <strong>Об ИИ-оценке:</strong> Ваше описание и фотографии будут обработаны
    Google Gemini AI через сервис OpenRouter. Данные передаются в зашифрованном виде
    и не сохраняются третьими сторонами после генерации ответа. Результат —
    ориентировочная оценка, не замена профессиональному осмотру.
    <a href="/privacy/#ai-processing" class="underline ml-1">Подробнее</a>
  </p>
</div>
```

**Вариант Б — Модальное окно при первом взаимодействии с формой**
Показывать popup-уведомление при первом клике на любое поле формы с кратким объяснением ИИ-обработки. Сохранять факт показа в `sessionStorage`.

**Вариант В — Раздел в политике конфиденциальности + ссылка из формы**
Добавить якорь `#ai-processing` в Privacy Policy с полным описанием: какие данные передаются, кому (OpenRouter, Google), на каких условиях, ссылки на их политики. В форме разместить ссылку на этот якорь.

---

### 7. Отсутствует раскрытие Cal.com на странице бронирования

**Нарушает:** GDPR ст. 13 (уведомление о передаче данных третьим лицам)
**Файл:** `templates/booking/index.html`

Сайт интегрирует Cal.com (виджет бронирования), который собирает и хранит имя, email, телефон и предпочтительное время пользователей. Пользователь не уведомлён об этом.

---

#### Варианты решения:

**Вариант А — Уведомление под виджетом (15 минут)**

```html
<!-- templates/booking/index.html — добавить после cal-embed контейнера -->
<p class="text-xs text-gray-400 text-center mt-4">
  Бронирование обрабатывается сервисом Cal.com. Ваши данные хранятся на серверах Cal.com
  согласно их
  <a href="https://cal.com/privacy" target="_blank" rel="noopener" class="underline">
    Политике конфиденциальности
  </a>.
</p>
```

**Вариант Б — Раздел в собственной политике конфиденциальности**
Добавить Cal.com в раздел «Сторонние обработчики данных» в Privacy Policy с кратким описанием и ссылкой. Пользователи, читающие политику, узнают об этом.

---

### 8. Google Fonts передаёт IP-адреса пользователей

**Нарушает:** GDPR (IP-адрес — персональные данные по законодательству ЕС)
**Файл:** `templates/base.html` — загрузка шрифта Inter с `fonts.googleapis.com`

При каждой загрузке страницы браузер пользователя делает запрос к серверам Google, передавая IP-адрес. Google может отслеживать посещения.

---

#### Варианты решения:

**Вариант А — Самостоятельный хостинг шрифта (1 час, рекомендуется)**
Скачать Inter с [Google Fonts Helper](https://gwfh.mranftl.com/fonts/inter), разместить в `static/fonts/`, обновить CSS.

```css
/* static/css/fonts.css */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400 800;
  font-display: swap;
  src: url('/static/fonts/inter-v20-latin-regular.woff2') format('woff2');
}
```

```html
<!-- base.html — заменить Google Fonts блок на: -->
<link rel="stylesheet" href="{% static 'css/fonts.css' %}">
```

**Вариант Б — Системные шрифты (0 часов, без CDN)**
Заменить `font-family: 'Inter'` на `font-family: system-ui, -apple-system, sans-serif` в Tailwind-конфиге. Inter установлен на большинстве современных macOS/iOS, на Windows используется Segoe UI.

**Вариант В — Загрузка Google Fonts после согласия (сложнее)**
Блокировать загрузку шрифта до получения cookie-согласия, затем динамически добавлять `<link>`. Технически сложнее и ухудшает UX при первой загрузке — не рекомендуется.

---

### 9. Нет юридических ссылок в футере и навигации

**Нарушает:** GDPR требует «легкодоступности» политики конфиденциальности

**Файл:** `templates/base.html` — футер содержит только ссылки на демо-страницы, без юридических документов.

---

#### Варианты решения:

**Вариант А — Добавить ссылки в футер (15 минут)**

```html
<!-- templates/base.html — в блок футера -->
<div class="border-t border-gray-700 mt-8 pt-6 flex flex-wrap gap-4 text-xs text-gray-400">
  <a href="/privacy/" class="hover:text-white">Политика конфиденциальности</a>
  <a href="/terms/"   class="hover:text-white">Условия использования</a>
  <a href="/cookies/" class="hover:text-white">Cookie-политика</a>
</div>
```

**Вариант Б — Добавить в хедер навигацию с выпадающим меню «Правовая информация»**
Для агентства, продающего услуги клиентам, видимость юридических документов повышает доверие — стоит разместить в шапке, а не только в футере.

---

### 10. IP-адрес собирается без раскрытия

**Нарушает:** GDPR (IP-адрес — персональные данные)
**Файлы:** `apps/quote/models.py`, `apps/web_quote/models.py` — поле `ip_address` хранится бессрочно

---

#### Варианты решения:

**Вариант А — Раскрыть в Privacy Policy + установить TTL**
Указать в политике: «IP-адрес собирается для защиты от злоупотреблений (rate limiting) и удаляется автоматически через 30 дней». Добавить в команду очистки из п. 5.

**Вариант Б — Хранить хеш IP вместо самого адреса**
Вместо сырого IP хранить его SHA-256 хеш — rate limiting продолжает работать, но конкретный пользователь не идентифицируем (формально выходит из-под GDPR в качестве персональных данных).

```python
# apps/quote/views.py
import hashlib

def get_ip_hash(request):
    ip = request.META.get('REMOTE_ADDR', '')
    return hashlib.sha256(ip.encode()).hexdigest()

# При сохранении записи:
quote.ip_address = get_ip_hash(request)
```

**Вариант В — Полностью убрать хранение IP**
Если rate limiting реализован через Django cache (что уже сделано), IP можно вообще не сохранять в БД — только держать в кеше. Убрать поле `ip_address` из моделей, сделать миграцию.

---

## ВСЁ ХОРОШО ✅ — Соответствует требованиям

| Пункт | Подтверждение |
|---|---|
| Демо-характер сайта чётко обозначен | `base.html` футер: «All content is simulated for demonstration purposes only» |
| CSRF-защита на всех POST-запросах | `EnsureCsrfCookieMiddleware` + заголовок `X-CSRFToken` в каждом fetch |
| Rate limiting на ИИ-эндпоинтах | 5 запросов/час на IP в обоих квотных вьюхах |
| Фото не сохраняются на диск | `apps/quote/ai_service.py` — только base64, без записи файлов |
| Серверная валидация входных данных | Присутствует во всех вьюхах |
| Блог-контент санируется от XSS | Библиотека `bleach` в `ArticleDetailView` |
| Нет аналитики и трекинг-пикселей | Google Analytics, Meta Pixel, Mixpanel — не найдены |
| Оценки ИИ — диапазоны, не точные числа | `apps/quote/pricing.py` — юридически корректно, честно |
| Emergency-форма — симуляция без хранения | `EmergencySubmitView` не пишет в БД |
| Нет автопроигрывания медиа | Не обнаружено |

---

## Не применимо к данному проекту — N/A

| Требование | Причина |
|---|---|
| «Не продавать мои данные» (CCPA opt-out) | Данные не продаются третьим сторонам |
| CAN-SPAM / отписка | Email-маркетинг отсутствует |
| Политика возврата/отмены | Платёжная система отсутствует |
| HIPAA | Медицинские данные не собираются |
| Возрастная верификация | Нет контента с возрастными ограничениями |

---

## Топ-5 приоритетных задач

| # | Задача | Почему срочно | Оценка времени |
|---|---|---|---|
| 1 | **Политика конфиденциальности** | Сбор PII без политики — прямое нарушение GDPR/CCPA | 2–3 часа |
| 2 | **Чекбоксы согласия в формах** | Каждая отправка формы — нарушение GDPR ст. 7 | 30–60 мин |
| 3 | **Условия использования с оговоркой об ИИ** | Риск иска за доверие к ИИ-оценке | 1–2 часа |
| 4 | **Cookie-баннер** | `csrftoken` устанавливается без уведомления | 30–60 мин |
| 5 | **Удаление старых записей (90 дней)** | Бессрочное хранение PII нарушает GDPR ст. 5(1)(e) | 2–3 часа |

---

## Итоговый статус по регуляторам

```
GDPR (ЕС):         ❌ НЕ СООТВЕТСТВУЕТ — нет политики, согласия, хранения, прав субъектов
CCPA (Калифорния): ❌ НЕ СООТВЕТСТВУЕТ — нет политики, раскрытия прав
FTC (США):         ⚠️ ЧАСТИЧНО        — ИИ раскрыт частично, демо обозначено
EU AI Act 2024:    ⚠️ ЧАСТИЧНО        — ИИ присутствует, обработчик не раскрыт
ADA / WCAG 2.1:    ⚠️ НЕ ПРОВЕРЕНО   — формы имеют метки, но контрастность и клавиатурная навигация не тестировались
EAA (ЕС, 2025):    ⚠️ НЕ ПРОВЕРЕНО   — аналогично WCAG
```

---

## Оценка объёма работ

| Группа | Задачи | Суммарное время |
|---|---|---|
| Критические (запустить в первую очередь) | Privacy Policy, Terms, Cookie Banner, чекбоксы согласия, TTL/удаление | ~8–10 часов |
| Высокий приоритет (1–2 недели) | Ссылки в футере, Cal.com раскрытие, раскрытие ИИ, IP-хеширование | ~4–6 часов |
| Средний приоритет (1 месяц) | Самохостинг Google Fonts, API права субъекта, Accessibility-аудит | ~6–8 часов |
| **Итого** | | **~18–24 часа** |

---

## Приложение: Минимальный текст Privacy Policy (шаблон)

```markdown
# Политика конфиденциальности

**Последнее обновление:** [ДАТА]

## 1. Кто мы
[Название агентства], [адрес], [email для связи].

## 2. Какие данные мы собираем
- **Через формы:** имя, email, телефон, адрес, описание задачи
- **Автоматически:** IP-адрес (для защиты от злоупотреблений)
- **Cookie:** csrftoken (защита форм), sessionid (техническая сессия)

## 3. Для чего используются данные
- Генерация ИИ-оценок по вашему запросу
- Защита от злоупотреблений (rate limiting по IP)
- Улучшение качества демонстрационного сервиса

## 4. Передача данных третьим лицам
| Получатель | Цель | Политика |
|---|---|---|
| Google Gemini via OpenRouter | Генерация ИИ-оценок | [openrouter.ai/privacy] |
| Cal.com | Хранение записей на приём | [cal.com/privacy] |
| Cloudflare Turnstile | Защита форм от ботов | [cloudflare.com/privacypolicy] |
| Google Fonts | Загрузка шрифтов | [policies.google.com/privacy] |

## 5. Сроки хранения
- Данные форм (quote, web-quote): удаляются через 90 дней
- IP-адреса: удаляются через 30 дней
- Данные бронирований: хранятся Cal.com согласно их политике

## 6. Ваши права
Вы вправе: получить копию своих данных, потребовать их удаления,
ограничить обработку, получить данные в машиночитаемом формате.
Для реализации прав — напишите на [email].

## 7. Безопасность
Данные передаются по HTTPS. Доступ к БД ограничен.
Фотографии НЕ сохраняются — только передаются ИИ для генерации оценки.

## 8. Контакты
По вопросам конфиденциальности: [email]
```

---

*Документ сформирован на основе автоматического анализа кодовой базы проекта. Не является юридической консультацией. Для продакшен-деплоя рекомендуется проверка квалифицированным юристом.*
