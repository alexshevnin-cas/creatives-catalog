# Creatives Catalog — Техническое задание

> **Версия:** 1.1
> **Дата:** 2026-03-20
> **Статус:** Готово к разработке
> **Прототип:** https://alexshevnin-cas.github.io/creatives-catalog/
> **Источники:** product-spec.md v1.1, интервью Novatska + Shyfrin + Zoriana, рабочий прототип

---

## 1. Контекст

Прототип каталога реализован и валидирован. Настоящий документ — ТЗ для разработки production-версии.

**Что решает система:**
- Дизайнер загружает файл → система автоматически именует по конвенции → файл попадает в каталог и на сервер CAS
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
| Backend | Python + FastAPI | Знакомый стек команды, async |
| Database | PostgreSQL | Production-ready, полнотекстовый поиск |
| File storage | Сервер CAS (локальная FS) | Google Drive заканчивается (~100 ГБ), файлы хранятся на собственном сервере |
| Thumbnails | Pillow + ffmpeg | Генерация превью на сервере при загрузке (Pillow для изображений, ffmpeg для видео) |
| Frontend | React или Vue (на выбор команды) | SPA, быстрый интерфейс |
| Auth | Google OAuth 2.0 | Вся команда на Google Workspace |
| Deployment | Docker + внутренний сервер / Cloud Run |  |

### 2.2. Схема загрузки и хранения

```
Дизайнер → Каталог (форма: [Игра ▼] [Тип ▼] + файл + теги)
                ↓
           Backend:
             1. Генерирует имя по конвенции
             2. Определяет WxH и duration из файла
             3. Создаёт записи в БД (concept + rendition)
             4. Сохраняет файл на сервер CAS
                в папку: /storage/creatives/{код1С}_{shortname}/{Type}/
             5. Генерирует thumbnail (Pillow / ffmpeg)
                ↓
           Сервер CAS (структура хранения):
           /storage/creatives/
           └── 7448_CarCrash/
               ├── Video/
               │   ├── V001_7448_CarCrash_1920x1080_30s.mp4
               │   ├── V001_7448_CarCrash_1080x1920_30s.mp4
               │   └── ...
               ├── Banner/
               └── Playable/
           /storage/creatives/thumbnails/
               └── ... (авто-генерация)
```

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
| tags | text | DEFAULT '' | Comma-separated: "gameplay,mislead,UGC,seasonal" |
| concept_name | varchar(200) | NOT NULL | Сгенерированное имя ("V003_7448_CarCrash") |
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
| generated_name | varchar(300) | NOT NULL | "V003_7448_CarCrash_1920x1080_30s" |
| file_path | varchar(500) | | Путь к файлу на сервере |
| thumbnail_path | varchar(500) | | Путь к thumbnail на сервере |
| file_size_mb | numeric(10,2) | | |
| original_filename | varchar(300) | | Исходное имя файла |
| created_at | timestamptz | DEFAULT now() | |

### 3.4. users

| Поле | Тип | Constraints | Описание |
|------|-----|------------|----------|
| id | serial | PK | |
| email | varchar(200) | UNIQUE, NOT NULL | Google Workspace email |
| name | varchar(200) | NOT NULL | |
| role | enum | DEFAULT 'designer' | designer / coordinator / ua_manager / cmo / admin |

---

## 4. Нейминговая конвенция

### 4.1. Формат

**Concept name** (без размеров):

| Тип | Формат | Пример |
|-----|--------|--------|
| Video | `V{NNN}_{код1С}_{shortname}` | `V003_7448_CarCrash` |
| Banner | `B{NNN}_{код1С}_{shortname}` | `B011_7448_CarCrash` |
| Playable | `PLAY_{NNN}_{код1С}_{shortname}` | `PLAY_001_7448_CarCrash` |

**Rendition name** (полное имя файла):

| Тип | Формат | Пример |
|-----|--------|--------|
| Video | `{concept}_{WxH}_{duration}s` | `V003_7448_CarCrash_1920x1080_30s` |
| Banner | `{concept}_{WxH}` | `B011_7448_CarCrash_1020x500` |
| Playable | `{concept}` | `PLAY_001_7448_CarCrash` |

### 4.2. Правила

- `NNN` — трёхзначный порядковый номер, автоинкремент per game + type
- Сезонность **не включается в имя** — вместо этого используются теги (`gameplay`, `mislead`, `UGC`, `seasonal`)
- Сезонная вариация = новый концепт (новый порядковый номер)
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
| GET | `/api/creatives` | Список с фильтрами (?game_id, ?type, ?status, ?tags, ?search) |
| GET | `/api/creatives/{id}` | Детали концепта с рендициями |
| POST | `/api/creatives` | Создать концепт (quick-add, без файла) |
| PATCH | `/api/creatives/{id}/status` | Изменить статус |
| PATCH | `/api/creatives/{id}/networks` | Toggle сети |
| PATCH | `/api/creatives/{id}/tags` | Toggle теги (аналогично сетям) |
| DELETE | `/api/creatives/{id}` | Удалить (каскадно с рендициями + файлы с сервера) |

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
  "generated_name": "V003_7448_CarCrash_1920x1080_30s",
  "width": 1920,
  "height": 1080,
  "duration_sec": 30,
  "file_path": "/storage/creatives/7448_CarCrash/Video/V003_7448_CarCrash_1920x1080_30s.mp4",
  "thumbnail_path": "/storage/creatives/thumbnails/V003_7448_CarCrash_1920x1080_30s.jpg"
}
```

Backend при загрузке:
1. Определяет width/height/duration из файла (Pillow для картинок, ffprobe для видео)
2. Генерирует rendition name
3. Сохраняет файл на сервер CAS в правильную папку
4. Генерирует thumbnail (Pillow для изображений, ffmpeg для видео — первый кадр)
5. Сохраняет в БД

---

## 6. UI / Страницы

### 6.1. Каталог (главная)

Древовидный список: **Игра → Тип → Концепт → Рендиции**

Столбцы концепта:
| # | Теги | Превью | Концепт | Файлы | Сети | Статус |
|---|------|--------|---------|-------|------|--------|

- **#** — порядковый номер (012, 011, ...)
- **Теги** — кликабельные бейджи (`gameplay`, `mislead`, `UGC`, `seasonal` и др.)
- **Превью** — thumbnail (генерируется на сервере)
- **Файлы** — раскрывающийся список рендиций (разные разрешения)
- **Сети** — кликабельные бейджи (Mintegral, FB, TikTok, Google Ads)
- **Статус** — дропдаун (Draft → Ready → Active → Archived)
- Сортировка: новые концепты сверху (DESC по seq_number)
- Фильтры: игра, тип, теги, статус, поиск по имени
- Кнопка **+ Добавить** в строке типа — открывает модалку с предзаполненными полями

### 6.2. Модалка добавления

Открывается из каталога (кнопка "+ Добавить" в строке типа):

- Игра и тип предзаполнены (можно поменять)
- Мульти-селект тегов (`gameplay`, `mislead`, `UGC`, `seasonal` и др.)
- Drag & drop файла
- Размеры и длительность определяются автоматически
- Live-preview сгенерированного имени
- Кнопка "Добавить"

### 6.3. Справочник игр

Таблица с inline-редактированием:
- Код 1С, Название, Short name, Платформа
- Добавление / редактирование / удаление

---

## 7. Хранилище файлов

### 7.1. Решение: собственный сервер

Google Drive заканчивается (~100 ГБ занято + ~130 ГБ от двух крупных игр на подходе). Файлы хостятся на серверах CAS.

**Открытый вопрос:** стоимость 1 ТБ на сервере vs Google Drive Business — узнать у Вовы.

### 7.2. Структура хранения

```
/storage/creatives/
├── 7448_CarCrash/
│   ├── Video/
│   │   ├── V001_7448_CarCrash_1920x1080_30s.mp4
│   │   ├── V001_7448_CarCrash_1080x1920_30s.mp4
│   │   └── V001_7448_CarCrash_1280x720_15s.mp4
│   ├── Banner/
│   └── Playable/
├── 8901_MergeKingdom/
│   └── ...
├── thumbnails/
│   └── ... (авто-генерация)
```

### 7.3. Операции

| Операция | Реализация | Когда |
|----------|-----------|-------|
| Создать папку игры | `os.makedirs` | При создании игры в справочнике |
| Создать папку типа | `os.makedirs` | При первом креативе данного типа |
| Сохранить файл | Запись на диск | При добавлении рендиции |
| Сгенерировать thumbnail | Pillow / ffmpeg | После загрузки файла |
| Удалить файл | `os.remove` | При удалении рендиции |

### 7.4. Thumbnails

Генерируются на сервере при загрузке:
- **Изображения** (.png, .jpg, .webp) — resize через Pillow
- **Видео** (.mp4, .mov, .webm) — первый кадр через ffmpeg
- Хранятся в `/storage/creatives/thumbnails/`

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

| Роль | Кто | Может делать |
|------|-----|-------------|
| designer | Дизайнеры | Загружать файлы, видеть каталог |
| coordinator | Hanna | Всё что designer + менять статусы, менять сети, менять теги |
| ua_manager | Vitalii Tereshchenko | Всё что coordinator + заливка на сети (V1.2), видит перформанс |
| cmo | Zoriana Omelchuk | Просмотр каталога, фильтры, превью — быстрый ответ на вопросы CEO |
| admin | — | Всё + управление справочником игр и пользователями |

Авторизация через Google OAuth 2.0. Роли назначаются в БД (таблица users).

---

## 10. Этапы реализации

### V1.0 — Хранилище + каталог (заменяет Google Drive)

- [ ] Backend: FastAPI + PostgreSQL + модель данных
- [ ] API: CRUD games, creatives, renditions
- [ ] Хранилище файлов на сервере CAS (upload + thumbnails через Pillow/ffmpeg)
- [ ] Загрузка файлов с авто-определением размеров (ffprobe + Pillow)
- [ ] Автонейминг по конвенции (без сезонности в имени)
- [ ] Теги (`gameplay`, `mislead`, `UGC`, `seasonal` и др.)
- [ ] Frontend: каталог (дерево), фильтры, поиск
- [ ] Модалка добавления с drag & drop + мульти-селект тегов
- [ ] Справочник игр (код 1С + short_name)
- [ ] Google OAuth 2.0
- [ ] Docker + deploy

### V1.2 — Автозаливка на сети через API

- [ ] Кнопка «Залить на Meta / Google / TikTok / Unity»
- [ ] API интеграция с рекламными сетями (у Vitalii Tereshchenko есть креды и аккаунты)
- [ ] YouTube: заливка видео по API → менеджер выбирает по имени в кампании
- [ ] Meta: каталог ассетов через API

### V2+ — Аналитика по креативам

- Маркетинговые метрики: Impression → Click → Install конверсии, Spend vs ROAS
- Кросс-креативные сравнения: mislead vs non-mislead
- Продуктовые метрики на креатив: Retention по когорте
- Маппинг старых креативов
- Интеграция с 1С для автосинхронизации справочника игр

---

## 11. Принятые решения

| # | Решение | Обоснование |
|---|---------|-------------|
| D1 | Сеть НЕ в имени | Источник определяется через MMP (Shyfrin) |
| D2 | ~~Сезонность — фиксированная позиция после номера~~ → **убрана из нейминга**, заменена тегом `seasonal` | Zoriana + Alexei (2026-03-19) |
| D3 | Старые креативы не переименовывать | Потеря перформанса в сетях (Shyfrin) |
| D4 | Сезонная вариация = новый концепт (новый порядковый номер) | Shyfrin (2026-03-16) |
| D5 | ~~Google Drive как хранилище~~ → **собственный сервер** (Drive заканчивается) | Zoriana (2026-03-19) |
| D6 | Thumbnails генерируются на сервере (Pillow/ffmpeg) | Zoriana (2026-03-19) |
| D7 | Три типа: Video, Banner, Playable (StoreVideo убран) | Валидация на прототипе |
| D8 | Размеры и длительность — авто-определение из файла | Валидация на прототипе |
| D9 | Каталог, не бот — однозначно | Zoriana (2026-03-19) |
| D10 | Теги вместо сезонности: `gameplay`, `mislead`, `UGC`, `seasonal` | Zoriana (2026-03-19) |
| D11 | Фазирование: V1.0 (хранилище+каталог) → V1.2 (API сети) → V2+ (аналитика) | Zoriana (2026-03-19) |

---

## 12. Ссылки

| Ресурс | URL |
|--------|-----|
| Прототип (статика) | https://alexshevnin-cas.github.io/creatives-catalog/ |
| Репозиторий прототипа | https://github.com/alexshevnin-cas/creatives-catalog |
| Продуктовая спецификация | `docs/product-spec.md` |
| Интервью Novatska | `research/interview-novatska.md` |
| Интервью Shyfrin | `research/interview-shyfrin.md` |
| Интервью Zoriana | `research/interview-zoriana.md` |
