# Creatives Catalog — Техническое задание

> **Версия:** 1.0
> **Дата:** 2026-03-18
> **Статус:** Готово к разработке
> **Прототип:** https://alexshevnin-cas.github.io/creatives-catalog/
> **Источники:** product-spec.md, интервью Novatska + Shyfrin, рабочий прототип

---

## 1. Контекст

Прототип каталога реализован и валидирован. Настоящий документ — ТЗ для разработки production-версии.

**Что решает система:**
- Дизайнер загружает файл → система автоматически именует по конвенции → файл попадает в каталог и на Google Drive
- Единое имя в каталоге = имя в Superset → аналитика не ломается
- Координатор больше не бутылочное горлышко в нейминге

**Что валидировано прототипом:**
- Древовидный каталог: Игра → Тип → Концепт → Рендиции
- Автонейминг по конвенции (дропдауны, без ручного ввода)
- Авто-определение размеров и длительности из файла
- Статусы, сети, фильтры, поиск

---

## 2. Архитектура

### 2.1. Стек

| Компонент | Технология | Обоснование |
|-----------|-----------|-------------|
| Backend | Python + FastAPI | Знакомый стек команды, async для Google Drive API |
| Database | PostgreSQL | Production-ready, полнотекстовый поиск |
| File storage | Google Drive API v3 | Дизайнеры уже работают в Drive, не ломаем процесс |
| Thumbnails | Google Drive thumbnailLink | Drive генерирует превью для видео и картинок — не храним локально |
| Frontend | React или Vue (на выбор команды) | SPA, быстрый интерфейс |
| Auth | Google OAuth 2.0 | Вся команда на Google Workspace |
| Deployment | Docker + внутренний сервер / Cloud Run |  |

### 2.2. Схема интеграции с Google Drive

```
Дизайнер → Каталог (форма: игра + тип + сезон + файл)
                ↓
           Backend:
             1. Генерирует имя по конвенции
             2. Определяет WxH и duration из файла
             3. Создаёт записи в БД (concept + rendition)
             4. Загружает файл на Google Drive
                в папку: /{Game}/{Type}/{ConceptFolder}/
             5. Получает thumbnailLink из Drive API
                ↓
           Google Drive (структура папок):
           └── CarCrash/
               ├── Video/
               │   ├── V001/
               │   │   ├── V001_7448_CarCrash_1920x1080_30s.mp4
               │   │   └── V001_7448_CarCrash_1080x1920_30s.mp4
               │   └── V002UE/
               ├── Banner/
               └── Playable/
```

### 2.3. Альтернативный flow: загрузка из Drive

```
Дизайнер → кладёт файл в входящую папку на Drive (как привыкли)
                ↓
           Watcher (cron / Drive push notifications):
             1. Обнаруживает новый файл
             2. По папке определяет игру
             3. Просит дизайнера через UI выбрать тип + сезонность
                (или определяет автоматически по правилам)
             4. Генерирует имя, переименовывает в Drive
             5. Создаёт запись в каталоге
```

> **Рекомендация:** реализовать оба flow. Основной — через форму каталога. Фоновый watcher — как бонус, чтобы подхватывать файлы, загруженные напрямую в Drive.

---

## 3. Модель данных

### 3.1. games

| Поле | Тип | Constraints | Описание |
|------|-----|------------|----------|
| id | serial | PK | |
| code_1c | varchar(20) | UNIQUE, NOT NULL | Код из 1С ("7448") |
| name | varchar(200) | NOT NULL | Полное название ("Car Crash Simulator") |
| short_name | varchar(50) | NOT NULL | Для нейминга ("CarCrash") |
| platform | enum | DEFAULT 'Both' | Android / iOS / Both |
| created_at | timestamptz | DEFAULT now() | |

### 3.2. creatives (concept)

| Поле | Тип | Constraints | Описание |
|------|-----|------------|----------|
| id | serial | PK | |
| game_id | int | FK → games, NOT NULL | |
| type | enum | NOT NULL | Video / Banner / Playable |
| seq_number | int | NOT NULL | Порядковый номер концепта |
| seasonal_tag | varchar(10) | DEFAULT 'STD' | STD / UE / NY / EA |
| concept_name | varchar(200) | NOT NULL | Сгенерированное имя ("V003UE_7448_CarCrash") |
| status | enum | DEFAULT 'Draft' | Draft / Ready / Active / Archived |
| networks | varchar(200) | DEFAULT '' | Comma-separated: "Mintegral,FB,TikTok" |
| description | text | | Описание концепта |
| created_at | timestamptz | DEFAULT now() | |
| created_by | int | FK → users | Кто создал |
| | | UNIQUE(game_id, type, seq_number) | |

### 3.3. renditions

| Поле | Тип | Constraints | Описание |
|------|-----|------------|----------|
| id | serial | PK | |
| creative_id | int | FK → creatives ON DELETE CASCADE | |
| width | int | | Ширина (px) |
| height | int | | Высота (px) |
| duration_sec | int | | Для видео |
| generated_name | varchar(300) | NOT NULL | "V003UE_7448_CarCrash_1920x1080_30s" |
| drive_file_id | varchar(100) | | Google Drive file ID |
| drive_thumbnail_url | text | | thumbnailLink из Drive API |
| file_size_mb | numeric(10,2) | | |
| original_filename | varchar(300) | | Исходное имя файла |
| created_at | timestamptz | DEFAULT now() | |

### 3.4. users

| Поле | Тип | Constraints | Описание |
|------|-----|------------|----------|
| id | serial | PK | |
| email | varchar(200) | UNIQUE, NOT NULL | Google Workspace email |
| name | varchar(200) | NOT NULL | |
| role | enum | DEFAULT 'designer' | designer / coordinator / manager / admin |

---

## 4. Нейминговая конвенция

### 4.1. Формат

**Concept name** (без размеров):

| Тип | Формат | Пример |
|-----|--------|--------|
| Video | `V{NNN}{seasonal}_{код1С}_{shortname}` | `V003UE_7448_CarCrash` |
| Banner | `B{NNN}{seasonal}_{код1С}_{shortname}` | `B011_7448_CarCrash` |
| Playable | `PLAY_{NNN}{seasonal}_{код1С}_{shortname}` | `PLAY_001_7448_CarCrash` |

**Rendition name** (полное имя файла):

| Тип | Формат | Пример |
|-----|--------|--------|
| Video | `{concept}_{WxH}_{duration}s` | `V003UE_7448_CarCrash_1920x1080_30s` |
| Banner | `{concept}_{WxH}` | `B011_7448_CarCrash_1020x500` |
| Playable | `{concept}` | `PLAY_001_7448_CarCrash` |

### 4.2. Правила

- `NNN` — трёхзначный порядковый номер, автоинкремент per game + type
- `seasonal` — пусто для STD, иначе `UE`/`NY`/`EA` сразу после номера без `_`
- Только ASCII, разделитель `_`, без пробелов и кириллицы
- Размеры и длительность определяются из файла автоматически
- Сеть НЕ включается в имя (источник из MMP)

---

## 5. API Endpoints

### 5.1. Games

| Method | Path | Описание |
|--------|------|----------|
| GET | `/api/games` | Список всех игр |
| POST | `/api/games` | Создать игру |
| PUT | `/api/games/{id}` | Обновить игру |
| DELETE | `/api/games/{id}` | Удалить (если нет креативов) |

### 5.2. Creatives (concepts)

| Method | Path | Описание |
|--------|------|----------|
| GET | `/api/creatives` | Список с фильтрами (?game_id, ?type, ?status, ?seasonal, ?search) |
| GET | `/api/creatives/{id}` | Детали концепта с рендициями |
| POST | `/api/creatives` | Создать концепт (quick-add, без файла) |
| PATCH | `/api/creatives/{id}/status` | Изменить статус |
| PATCH | `/api/creatives/{id}/networks` | Toggle сети |
| DELETE | `/api/creatives/{id}` | Удалить (каскадно с рендициями + файлы из Drive) |

### 5.3. Renditions

| Method | Path | Описание |
|--------|------|----------|
| POST | `/api/creatives/{id}/renditions` | Загрузить файл (новая рендиция) |
| DELETE | `/api/renditions/{id}` | Удалить рендицию |

### 5.4. Upload flow

```
POST /api/creatives/{id}/renditions
Content-Type: multipart/form-data
Body: file

Response:
{
  "id": 42,
  "generated_name": "V003UE_7448_CarCrash_1920x1080_30s",
  "width": 1920,
  "height": 1080,
  "duration_sec": 30,
  "drive_file_id": "1a2b3c...",
  "drive_thumbnail_url": "https://lh3.googleusercontent.com/..."
}
```

Backend при загрузке:
1. Определяет width/height/duration из файла (Pillow для картинок, ffprobe для видео)
2. Генерирует rendition name
3. Загружает на Google Drive в правильную папку
4. Получает thumbnailLink
5. Сохраняет в БД

---

## 6. UI / Страницы

### 6.1. Каталог (главная)

Древовидный список: **Игра → Тип → Концепт → Рендиции**

Столбцы концепта:
| # | Сезон | Превью | Концепт | Файлы | Сети | Статус |
|---|-------|--------|---------|-------|------|--------|

- **#** — порядковый номер (012, 011, ...)
- **Превью** — thumbnail из Google Drive
- **Файлы** — раскрывающийся список рендиций (разные разрешения)
- **Сети** — кликабельные бейджи (Mintegral, FB, TikTok, Google Ads)
- **Статус** — дропдаун (Draft → Ready → Active → Archived)
- Сортировка: новые концепты сверху (DESC по seq_number)
- Фильтры: игра, тип, сезон, статус, поиск по имени
- Кнопка **+ Добавить** в строке типа — открывает модалку с предзаполненными полями

### 6.2. Модалка добавления

Открывается из каталога (кнопка "+ Добавить" в строке типа):

- Игра и тип предзаполнены (можно поменять)
- Сезонность — дропдаун (STD по умолчанию)
- Drag & drop файла
- Размеры и длительность определяются автоматически
- Live-preview сгенерированного имени
- Кнопка "Добавить"

### 6.3. Справочник игр

Таблица с inline-редактированием:
- Код 1С, Название, Short name, Платформа
- Добавление / редактирование / удаление

---

## 7. Google Drive интеграция

### 7.1. Авторизация

- Service Account с доступом к shared Drive (или к конкретной папке)
- Или OAuth 2.0 от имени сервисного пользователя

### 7.2. Структура папок

```
[Root Folder: Creatives]/
├── CarCrash (7448)/
│   ├── Video/
│   │   ├── V001_7448_CarCrash/
│   │   │   ├── V001_7448_CarCrash_1920x1080_30s.mp4
│   │   │   ├── V001_7448_CarCrash_1080x1920_30s.mp4
│   │   │   └── V001_7448_CarCrash_1280x720_15s.mp4
│   │   └── V002UE_7448_CarCrash/
│   ├── Banner/
│   └── Playable/
├── MergeKingdom (8901)/
│   └── ...
```

### 7.3. Операции

| Операция | Drive API | Когда |
|----------|----------|-------|
| Создать папку игры | `files.create` (mimeType folder) | При создании игры в справочнике |
| Создать папку типа | `files.create` | При первом креативе данного типа |
| Загрузить файл | `files.create` (media upload) | При добавлении рендиции |
| Получить thumbnail | `files.get` (fields: thumbnailLink) | После загрузки файла |
| Удалить файл | `files.delete` | При удалении рендиции |
| Переименовать | `files.update` (name) | Если меняется сезонность |

### 7.4. Кеширование thumbnails

- `thumbnailLink` из Drive протухает через несколько часов
- Обновлять при загрузке каталога (batch запрос к Drive API)
- Или кешировать: скачивать thumbnail, хранить в CDN/S3, обновлять по cron

---

## 8. Определение размеров и длительности

Файл загружается через backend. Сервер определяет метаданные автоматически:

| Тип файла | Библиотека | Что определяем |
|-----------|-----------|----------------|
| Изображения (.png, .jpg, .webp) | Pillow | width, height |
| Видео (.mp4, .mov, .webm) | ffprobe (ffmpeg) | width, height, duration |
| Playable (.html, .zip) | — | Ничего (нет размеров) |

**ffprobe** — единственная внешняя зависимость. Установить в Docker-образ:
```dockerfile
RUN apt-get install -y ffmpeg
```

---

## 9. Роли и доступ

| Роль | Может делать |
|------|-------------|
| designer | Загружать файлы, видеть каталог |
| coordinator | Всё что designer + менять статусы, менять сети |
| manager | Всё что coordinator + удалять креативы |
| admin | Всё + управление справочником игр и пользователями |

Авторизация через Google OAuth 2.0. Роли назначаются в БД (таблица users).

---

## 10. Этапы реализации

### Этап 1: MVP (2-3 недели)

- [ ] Backend: FastAPI + PostgreSQL + модель данных
- [ ] API: CRUD games, creatives, renditions
- [ ] Загрузка файлов с авто-определением размеров (ffprobe + Pillow)
- [ ] Автонейминг по конвенции
- [ ] Frontend: каталог (дерево), фильтры, поиск
- [ ] Модалка добавления с drag & drop
- [ ] Google OAuth 2.0
- [ ] Docker + deploy

### Этап 2: Google Drive (1-2 недели)

- [ ] Интеграция с Google Drive API
- [ ] Автосоздание папок при загрузке
- [ ] Thumbnails из Drive API
- [ ] Скачивание файлов через Drive

### Этап 3: Улучшения (1 неделя)

- [ ] Батчевая загрузка (несколько файлов за раз → несколько рендиций)
- [ ] Drag & drop нескольких файлов
- [ ] Уведомления (Slack/Telegram) при новом креативе
- [ ] Логирование действий (кто что менял)

### Не входит в скоуп (V2+)

- Автозаливка на рекламные сети через API
- Перформанс-данные из Superset в карточке креатива
- A/B-группы
- Маппинг старых креативов
- Drive watcher (фоновый импорт из Drive)

---

## 11. Принятые решения

| # | Решение | Обоснование |
|---|---------|-------------|
| D1 | Сеть НЕ в имени | Источник определяется через MMP (Shyfrin) |
| D2 | Сезонность — фиксированная позиция после номера | Консистентный парсинг (Shyfrin) |
| D3 | Старые креативы не переименовывать | Потеря перформанса в сетях |
| D4 | Google Drive как хранилище | Дизайнеры уже там, не ломаем процесс |
| D5 | Thumbnails из Drive API | Не нужен ffmpeg для превью, Drive сам генерит |
| D6 | Три типа: Video, Banner, Playable | StoreVideo убран по результатам валидации |

---

## 12. Ссылки

| Ресурс | URL |
|--------|-----|
| Прототип (статика) | https://alexshevnin-cas.github.io/creatives-catalog/ |
| Репозиторий прототипа | https://github.com/alexshevnin-cas/creatives-catalog |
| Продуктовая спецификация | `docs/product-spec.md` |
| Интервью Novatska | `research/interview-novatska.md` |
| Интервью Shyfrin | `research/interview-shyfrin.md` |
