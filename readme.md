# TeamFinder

## О проекте

**TeamFinder** — веб-приложение для поиска команды под pet-проекты.
Пользователи публикуют проекты, находят участников и откликаются на чужие проекты.

## Основные возможности

- регистрация, вход и выход;
- профиль пользователя (контакты, описание, проекты);
- редактирование профиля и смена пароля;
- создание, редактирование и завершение проекта;
- участие в проектах;
- избранные проекты;
- список пользователей с фильтрами.

## Стек

- Python 3.13
- Django 5.2
- PostgreSQL 16
- Docker Compose
- Pillow
- HTML/CSS/JS

## Запуск

### 1. Клонирование

```bash
git clone <url-репозитория>
cd team-finder-ad
```

### 2. Виртуальное окружение

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

### 3. Настройка `.env`

```powershell
Copy-Item .env_example .env
```

Пример:

```env
DJANGO_SECRET_KEY=<your_secret_key>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5436
```

Генерация ключа:

```bash
py -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. PostgreSQL

```bash
docker compose up -d
```

Остановка:

```bash
docker compose down
```

### 5. Миграции и запуск

```bash
py manage.py migrate
py manage.py runserver
```

Приложение: http://127.0.0.1:8000/

## Тесты

```bash
py manage.py test
```

## Автор

- Иван
- GitHub: `kapustinI`
