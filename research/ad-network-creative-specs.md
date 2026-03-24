# Требования рекламных сетей к креативам

**Дата:** 2026-03-24
**Цель:** Определить ограничения по размерам, форматам, весу и длине имени для каждой сети

---

## Сводная таблица

### Длина имени креатива (ad name / creative name)

| Сеть | Лимит символов | Примечание |
|------|---------------|-----------|
| Meta (Facebook/Instagram) | 255 | Внутреннее имя в Ads Manager |
| Google Ads / CM360 | 255 | Ad name и creative name |
| TikTok | 40 (app/brand name) | Ad description до 100 символов |
| Unity Ads | Не документировано | Уточнить |
| Mintegral | Не документировано | Уточнить |

**Вывод по неймингу:** Наш максимальный нейминг ~45 символов (e.g. `V003_7448_CarCrash_1920x1080_30s_a1b2c3UA`). Вписывается во все документированные лимиты. TikTok может обрезать при отображении, но это app/brand name, а не имя файла.

---

### Video

| Параметр | Meta | Google Ads | TikTok | Unity Ads | Mintegral |
|----------|------|-----------|--------|-----------|-----------|
| **Форматы** | MP4, MOV | MP4 (через YouTube) | MP4, MOV, MPEG, 3GP, AVI | MP4 (H.264) | MP4 |
| **Макс. размер файла** | 4 ГБ | ~1 ГБ (рекомендация) | 500 МБ | 100 МБ (рек. 10 МБ) | Не документировано |
| **Разрешения** | 1080x1080, 1080x1350, 1080x1920 | Через YouTube (любое) | 1080x1920, 540x960+ | 1920x1080, 1080x1920 | 1920x1080, 1080x1920, 1280x720, 720x1280 |
| **Aspect ratio** | 1:1, 4:5, 9:16 | 16:9, 9:16, 1:1 | 9:16, 1:1, 16:9 | 16:9, 9:16 | 16:9, 9:16 |
| **Длительность** | До 240 мин | 6s (bumper), 15s (non-skip), до 3 мин (skippable) | До 10 мин (рек. 9-15s) | Рекомендуется 15-30s | 15-60s рекомендуется |

### Banner / Image

| Параметр | Meta | Google Ads | TikTok | Unity Ads | Mintegral |
|----------|------|-----------|--------|-----------|-----------|
| **Форматы** | JPG, PNG | JPG, PNG, GIF | JPG, PNG | PNG, JPG | JPG, PNG |
| **Макс. размер файла** | 30 МБ | 150 КБ (display) | 500 КБ | Не документировано | Не документировано |
| **Размеры** | 1080x1080, 1200x628 | 300x250, 728x90, 336x280 и др. | 1200x628 | 320x50, 728x90 | 1200x627, 1200x628, 512x512 |

### Playable

| Параметр | Unity Ads | Mintegral | Meta | Google Ads | TikTok |
|----------|-----------|-----------|------|-----------|--------|
| **Формат** | HTML (single file, MRAID 3.0) | HTML (single file) | HTML (single ZIP) | HTML5 ZIP | HTML |
| **Макс. размер** | 5 МБ | 5 МБ | 2 МБ (lead) + 5 МБ (demo) | 1 МБ (HTML5) | 2 МБ |

---

## Ключевые ограничения для нашего каталога

1. **Unity Ads — самый строгий по видео:** макс. 100 МБ (рекомендуется 10 МБ). Для Unity может потребоваться сжатие.
2. **Playables везде до 5 МБ** — single HTML file, всё inline.
3. **Имя креатива: 255 символов** в Meta и Google, у TikTok/Unity/Mintegral — не критично для имени файла, но уточнить для ad asset name.
4. **Основные разрешения видео:** 1920x1080, 1080x1920, 1080x1080 — покрывают 90% сетей.
5. **Основные разрешения баннеров:** 1200x628, 1080x1080, 300x250, 728x90.

---

## Источники

- [Meta Ads Guide](https://www.facebook.com/business/ads-guide/update)
- [Meta Ads Size Guide 2026](https://adsuploader.com/blog/meta-ads-size)
- [Google Ads Specs](https://support.google.com/google-ads/answer/13676244)
- [Google Ads Video Specs](https://support.google.com/google-ads/answer/13547298)
- [TikTok In-Feed Ads](https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads)
- [TikTok Ad Specs 2026](https://www.veuno.com/tiktok-ad-specs-your-guide-for-2026/)
- [Unity Ads Video Specs](https://docs.unity.com/acquire/en-us/manual/video-ads-specifications)
- [Unity Ads Playable Specs](https://docs.unity.com/en-us/grow/acquire/creatives/playable/specifications)
- [Mintegral Creative Specs](https://helpcenter.mintegral.com/en/docs/asset-specs)
- [Mintegral Playable Guide](https://adv-new.mintegral.com/doc/en/creatives/playable.html)
