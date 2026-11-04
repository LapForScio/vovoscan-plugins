# Changelog

## 1.2.0

- Chapters carry when they came out (`span.chapterdate`, "November 4, 2026"; `units.item.date`).

## 1.1.0

- Categories: the catalog filter lists the site's genres (110, read from the homepage's `/genres/<slug>/`
  links). A chosen genre switches the catalog to `/genres/<slug>/page/<n>/`; browsing everything is unchanged.

## 1.0.0

First draft.

- Catalog (browse + search) through `/page/<n>/?s=<query>`, titles from `/manga/<slug>/`,
  chapter pages from `#readerarea img`.
