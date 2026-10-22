# Changelog

## 1.1.0

- Categories: the catalog filter offers MangaDex's tag list (`/manga/tag`, all 77 tags as the site names them),
  sent as `includedTags[]` together with search and language. Browse without a category is unchanged.

## 1.0.0

- Catalog (browse + search) through `/manga`, `availableTranslatedLanguage[]` set from the device's language.
- Titles with cover, description, authors, genres and status.
- Chapter lists through `/chapter` (language-filtered, ascending, first 100).
- Reader pages through `/at-home/server/:id` with `let` (`baseUrl`, `hash`).
