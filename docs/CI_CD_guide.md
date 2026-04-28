# CI/CD Guide

Этот файл описывает, как вручную усилить `CI/CD` для `Archerion`, не меняя репозиторий автоматически.

## Цель

Сделать pipeline более безопасным и полезным:

1. проверять lint и тесты до сборки;
2. отделить build от deploy;
3. убрать зависимость от demo-значений и случайных env;
4. оставить понятный rollback/checklist для ручного деплоя.

## Рекомендуемые стадии

Минимальный порядок стадий в `.gitlab-ci.yml`:

1. `lint`
2. `test`
3. `build`
4. `deploy`

## Что добавить в pipeline

### 1. Frontend lint

Команда:

```bash
cd frontend
npm ci
npm run lint
```

### 2. Backend lint

Команды:

```bash
cd backend
python -m pip install -r requirements.txt
python -m pip install ".[dev]"
ruff check .
black --check .
```

Если установка из `.[dev]` не используется в твоем окружении, можно поставить только:

```bash
pip install ruff black pre-commit
```

### 3. Backend tests

Команда:

```bash
cd backend
python manage.py test
```

Для стабильности лучше запускать тесты на `sqlite3`, если они не требуют внешнего Postgres/MinIO.

### 4. Optional frontend smoke checks

Если не хочешь пока добавлять e2e, достаточно:

```bash
cd frontend
npm ci
npm run build
```

Это даст раннюю проверку App Router и типовых ошибок сборки.

## Пример структуры `.gitlab-ci.yml`

Ниже не готовый файл для слепой вставки, а безопасный шаблон-ориентир:

```yaml
stages:
  - lint
  - test
  - build
  - deploy

frontend-lint:
  stage: lint
  script:
    - cd frontend
    - npm ci
    - npm run lint

backend-lint:
  stage: lint
  script:
    - cd backend
    - python -m pip install -r requirements.txt
    - python -m pip install ".[dev]"
    - ruff check .
    - black --check .

backend-tests:
  stage: test
  script:
    - cd backend
    - python -m pip install -r requirements.txt
    - python manage.py test

frontend-build:
  stage: build
  script:
    - docker compose build archerion_frontend

backend-build:
  stage: build
  script:
    - docker compose build archerion_backend

archerion-deploy:
  stage: deploy
  script:
    - docker compose up -d
  when: manual
```

## Secrets and env

Не клади реальные секреты в git.

Разделение лучше держать так:

- корневой `.env` - compose secrets и параметры контейнеров;
- `backend/.env` - backend runtime config;
- `healthcheck/.env` - только для отдельного запуска healthcheck вне compose, если нужен;
- в CI использовать masked/protected variables или file variables.

### Что вынести в GitLab variables

- `POSTGRES_PASSWORD`
- `MINIO_ROOT_PASSWORD`
- `PGADMIN_DEFAULT_PASSWORD`
- `HEALTHCHECK_SESSION_SECRET`
- `DJANGO_SECRET_KEY`
- production `ALLOWED_HOSTS`
- production `CORS_ALLOWED_ORIGINS`

## Pre-deploy checklist

Перед `docker compose up -d` проверь:

1. актуальны ли env-файлы и secrets;
2. что `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS` выставлены под реальный домен;
3. что `DEBUG=False`;
4. что demo-пароли и `change-me` нигде не остались;
5. что Swagger либо закрыт, либо отключен на проде;
6. что `HEALTHCHECK_SECURE_COOKIES=True`, если используется HTTPS;
7. что образ frontend/backend собрался без ошибок;
8. что reverse proxy конфиг соответствует реальному домену.

## Manual deploy flow

Рекомендуемый ручной порядок:

1. подтянуть изменения;
2. обновить env/secrets на сервере;
3. прогнать lint/tests локально или в CI;
4. выполнить `docker compose build`;
5. выполнить `docker compose up -d`;
6. проверить `/swagger/`, frontend, login, reader area, admin area;
7. проверить `healthcheck`.

## Rollback checklist

Если после выкладки что-то пошло не так:

1. вернуться на предыдущий git commit;
2. пересобрать только затронутые сервисы;
3. выполнить `docker compose up -d`;
4. проверить frontend, backend API, auth и healthcheck;
5. отдельно проверить, не были ли изменены env/secrets.

## Что можно сделать следующим шагом

Когда будешь готов автоматизировать pipeline уже в репозитории:

1. добавить отдельные `lint` и `test` jobs;
2. сделать `deploy` manual only;
3. добавить artifact/log retention для test output;
4. вынести production overrides в отдельный compose-файл;
5. добавить smoke-check job после deploy.
