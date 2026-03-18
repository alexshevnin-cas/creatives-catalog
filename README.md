# Creatives Catalog

Внутренний инструмент CAS.AI для управления рекламными креативами: единый каталог, автонейминг, превью.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Приложение запустится на http://localhost:5001

## Возможности

- **Автонейминг** — система генерирует имя по конвенции (`V003_7448_CarCrash_1920x1080_30s`)
- **Каталог** — список креативов с превью, фильтрами и поиском
- **Справочник игр** — CRUD для игр (код 1С, название, short_name)
- **Статусы** — Draft → Ready → Active → Archived
- **Авто-определение** — размеры и длительность определяются из файла автоматически

## Нейминговая конвенция

| Тип | Формат | Пример |
|-----|--------|--------|
| Video | `V{NNN}_{код_1С}_{appname}_{WxH}_{duration}` | `V003_7448_CarCrash_1920x1080_30s` |
| StoreVideo | `SV{NNN}_{код_1С}_{appname}_{WxH}_{duration}` | `SV001_7448_CarCrash_1920x1080_30s` |
| Banner | `B{NNN}_{код_1С}_{appname}_{WxH}` | `B011_7448_CarCrash_1020x500` |
| Playable | `PLAY_{NNN}_{код_1С}_{appname}` | `PLAY_001_7448_CarCrash` |

Сезонный маркер (UE/NY/EA) ставится после номера: `V003UE_7448_CarCrash_...`

## Стек

- Python 3 + Flask
- SQLite (локальная БД `creatives.db`)
- Pillow (thumbnails для изображений)
- Vanilla JS (авто-определение размеров, live-preview имени)

## Документация

| Файл | Описание |
|------|----------|
| `docs/product-spec.md` | Продуктовая спецификация (v0.2) — модель данных, user stories, конвенция, MVP scope |
| `research/interview-novatska.md` | Интервью с координатором креативов (2026-03-12) |
| `research/interview-shyfrin.md` | Техтребования от Borys Shyfrin (2026-03-16) |
