# TeamFinder (вариант 1): запуск и проверка

## Что реализовано

Проект реализован на Django + PostgreSQL.
Активный вариант задания: `TASK_VERSION=1`.

Поддержаны основные сценарии:
- регистрация / вход / выход,
- список проектов и детальная страница проекта,
- создание и редактирование проекта,
- завершение проекта владельцем,
- участие в проекте,
- избранные проекты,
- список пользователей с фильтрами варианта 1,
- профиль пользователя, редактирование профиля, смена пароля.

## 1. Подготовка окружения

1. Создайте виртуальное окружение:
```bash
py -m venv .venv
```

2. Активируйте его (PowerShell):
```bash
.venv\Scripts\Activate.ps1
```

3. Установите зависимости:
```bash
py -m pip install -r requirements.txt
```

## 2. Настройка `.env`

1. Скопируйте пример:
```powershell
Copy-Item .env_example .env
```

2. Заполните `.env`:

```env
DJANGO_SECRET_KEY=<your_secret_key>
DJANGO_DEBUG=True

POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5436

TASK_VERSION=1
```

3. Сгенерируйте секретный ключ Django:
```bash
py -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Если в `DJANGO_SECRET_KEY` есть символ `$`, замените его на `$$` в файле `.env` (для Docker Compose).

## 3. Запуск PostgreSQL (Docker)

В проекте используется контейнер `postgres:16`.
Проброс порта в `docker-compose.yml`: `5436:5432`.

Запуск:
```bash
docker compose up -d
```

Проверка:
```bash
docker ps
```

Остановка:
```bash
docker compose down
```

Сброс БД (если нужно полностью пересоздать данные):
```bash
docker compose down -v
docker compose up -d
```

## 4. Миграции и запуск Django

1. Примените миграции:
```bash
py manage.py migrate
```

2. Запустите сервер:
```bash
py manage.py runserver
```

Приложение будет доступно по адресу:
- http://127.0.0.1:8000/

## 5. Что проверить ревьюеру

1. Регистрация нового пользователя (`/users/register/`) и вход (`/users/login/`).
2. Создание проекта (`/projects/create-project/`).
3. Открытие карточки проекта (`/projects/<id>/`) и завершение проекта владельцем.
4. Добавление/удаление проекта в избранное и страница `/projects/favorites/`.
5. Список участников `/users/list/` и фильтры варианта 1:
   - `owners-of-favorite-projects`
   - `owners-of-participating-projects`
   - `interested-in-my-projects`
   - `participants-of-my-projects`
6. Редактирование профиля (`/users/edit-profile/`) и смена пароля (`/users/change-password/`).

## 6. Известные моменты

- Используется только вариант 1 (`TASK_VERSION=1`).
- Шаблоны для других вариантов оставлены в репозитории как часть стартового набора.
