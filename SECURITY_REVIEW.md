# Security Review

Дата: 2026-04-22

## Контекст

Проект состоит из:

- `backend` на Django/DRF
- `frontend` на Next.js
- `PostgreSQL`
- `MinIO`
- `pgAdmin`
- `healthcheck` с отдельным UI и авторизацией через backend-админа

Этот обзор сфокусирован на безопасности git-репозитория, конфигов и текущей проектной архитектуры перед выкладкой на сервер и домен.

## Основные риски

### 1. В репозитории хранится живой `.env` для `healthcheck` [✔️]

Файл:

- [healthcheck/.env](/home/lilwasd/Data/library/healthcheck/.env)

Проблема:

- в git хранится рабочий конфиг с внутренними адресами сервисов и session secret;
- это раскрывает внутреннюю топологию проекта;
- `HEALTHCHECK_SESSION_SECRET` при утечке позволяет подделывать сессии `healthcheck`.

Риск:

- высокий

Что сделать:

- убрать `healthcheck/.env` из git;
- оставить только `healthcheck/.env-example`;
- сгенерировать новый длинный случайный `HEALTHCHECK_SESSION_SECRET`.

### 2. Нужна строгая настройка `ALLOWED_HOSTS`

Файл:

- [backend/core/settings.py](/home/lilwasd/Data/library/backend/core/settings.py)

Текущее состояние:

- `ALLOWED_HOSTS` уже читается из env;
- в шаблоне backend-конфига теперь есть безопасный пример со списком хостов;
- риск остается, если в проде оставить слишком широкий список.

Проблема:

- слишком широкий список хостов оставляет риск host header атак;
- прод-окружение должно использовать только реальные домены и внутренние хосты, которые действительно нужны.

Риск:

- средний

Что сделать:

- держать `ALLOWED_HOSTS` только в env;
- указывать только реальные домены и нужные хосты.

### 3. Swagger открыт публично без авторизации

Файлы:

- [backend/swagger/swagger.py](/home/lilwasd/Data/library/backend/swagger/swagger.py)
- [backend/core/urls.py](/home/lilwasd/Data/library/backend/core/urls.py)

Проблема:

- `swagger` сейчас доступен публично;
- любой внешний пользователь получает карту API, маршруты, схемы запросов и ответов.

Риск:

- высокий

Что сделать:

- закрыть swagger для неавторизованных пользователей;
- или отключать swagger на проде через env-флаг.

### 4. Секреты должны оставаться вне `docker-compose.yml`

Файл:

- [docker-compose.yml](/home/lilwasd/Data/library/docker-compose.yml)

Текущее состояние:

- compose использует переменные из корневого `.env`;
- в репозитории оставлен `compose.secrets.env.example`, а не боевые значения.

Проблема:

- если реальные значения попадут в коммит или в проде останутся дефолтные примеры, их будет легко утечь;
- ротация и разделение секретов по окружениям пока не автоматизированы.

Риск:

- средний

Что сделать:

- не держать реальные пароли в git;
- использовать отдельные env/secrets для каждого окружения;
- сменить все demo-значения на случайные длинные перед выкладкой.

### 5. `healthcheck` раскрывает внутренние адреса и детали ошибок

Файлы:

- [healthcheck/server.py](/home/lilwasd/Data/library/healthcheck/server.py)
- [healthcheck/index.html](/home/lilwasd/Data/library/healthcheck/index.html)

Проблема:

- после входа пользователь видит внутренние адреса сервисов;
- отображаются технические детали типа сетевых ошибок и внутренних target URL.

Риск:

- средний

Что сделать:

- в проде показывать только `UP`, `WARN`, `DOWN`;
- скрыть внутренние URL и подробные сообщения об ошибках;
- подробную диагностику оставить только для приватного режима.

### 6. JWT хранится в `localStorage`

Файл:

- [frontend/src/lib/api.ts](/home/lilwasd/Data/library/frontend/src/lib/api.ts)

Проблема:

- `access_token` и `refresh_token` лежат в `localStorage`;
- при XSS они сразу будут украдены.

Риск:

- средний

Что сделать:

- для настоящего прод-режима перейти на `HttpOnly` cookies;
- либо очень жестко контролировать XSS-риск и CSP.

### 7. Dev-логика CORS может случайно открыть backend

Файл:

- [backend/core/settings.py](/home/lilwasd/Data/library/backend/core/settings.py)

Проблема:

- при `DEBUG=True` и пустом `CORS_ALLOWED_ORIGINS` включается `CORS_ALLOW_ALL_ORIGINS = True`;
- при ошибочном env прод может подняться со слишком открытым CORS.

Риск:

- средний

Что сделать:

- на проде всегда держать `DEBUG=False`;
- явно задавать `CORS_ALLOWED_ORIGINS`;
- не полагаться на fallback-логику.

### 8. MinIO-файлы по умолчанию помечаются как `public-read`

Файл:

- [backend/core/settings.py](/home/lilwasd/Data/library/backend/core/settings.py)

Текущее состояние:

```python
AWS_DEFAULT_ACL = "public-read"
```

Проблема:

- все загружаемые файлы могут становиться публично доступными;
- если туда позже попадут не только безопасные публичные файлы, будет утечка данных.

Риск:

- средний

Что сделать:

- перейти на приватные объекты;
- отдавать файлы через backend или подписанные URL.

## Дополнительные наблюдения

### `healthcheck` слушает `0.0.0.0`

Файл:

- [healthcheck/server.py](/home/lilwasd/Data/library/healthcheck/server.py)

Это нормально для контейнера за reverse proxy, но:

- наружу его без дополнительной защиты выставлять нельзя;
- для прод-режима нужно использовать HTTPS и `HEALTHCHECK_SECURE_COOKIES=True`.

### В проекте уже есть реальные меры доступа на API

Плюсы:

- у DRF по умолчанию стоит `IsAuthenticated`;
- часть admin-endpoint защищена `IsAdminUser`;
- `healthcheck` требует backend-логин администратора.

Это хорошо, но не закрывает инфраструктурные и конфигурационные риски выше.

## Что стоит сделать в первую очередь

### Приоритет 1

1. Удалить `healthcheck/.env` из git и сменить `HEALTHCHECK_SESSION_SECRET`.
2. Перевести `ALLOWED_HOSTS` в env и убрать `["*"]`.
3. Закрыть или отключить swagger на проде.
4. Убрать реальные пароли и секреты из `docker-compose.yml`.

### Приоритет 2

1. Скрыть внутренние адреса и технические ошибки в `healthcheck`.
2. Настроить `CSRF_TRUSTED_ORIGINS`.
3. Зафиксировать жесткий production CORS-list.
4. Включить secure cookies для `healthcheck` под HTTPS.

### Приоритет 3

1. Перевести frontend auth с `localStorage` на `HttpOnly` cookies.
2. Пересмотреть публичность MinIO-объектов.
3. Проверить git-history на уже утекшие секреты.

## Короткий вывод

Проект в текущем виде подходит для локальной разработки и демонстрации, но перед выкладкой на сервер и домен ему нужен hardening.

Критичные проблемы сейчас:

- секреты в репозитории;
- `ALLOWED_HOSTS = ["*"]`;
- публичный swagger;
- слабые секреты в compose.

Если эти пункты не закрыть, выкладывать проект в прод в открытый интернет не стоит.
