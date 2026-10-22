# MangaDex

MangaDex through its official API (`api.mangadex.org`): browse and search manga, chapter lists filtered by the
device's language, pages served by the at-home network.

## Settings: None

## What maps to what

- Catalog: `GET /manga?title=<search>&availableTranslatedLanguage[]=<lang>&includes[]=cover_art&limit=20&offset=<n>`.
  - Browsing (no search) returns the latest feed; `{{lang}}` is the device's language (empty value not sent).
  - Title: the first language entry (`attributes.title` is an object per language; many entries only have
    `ja-ro`).
  - Cover: the `cover_art` relationship's `fileName`, formatted as `https://uploads.mangadex.org/covers/<manga id>/<file>.256.jpg` (the item's own `{{id}}`).
  - `hasNext`: whether a 20th result came back (a full page means maybe more; the next empty page confirms).
- Title: `GET /manga/<id>?includes[]=cover_art` — name, cover, description (first available language), authors
  (`relationships[*].attributes.name`), genres (`tags[*].attributes.name`), `status` as MangaDex reports it.
- Units: `GET /chapter?manga=<id>&translatedLanguage[]=<lang>&limit=100&order[chapter]=asc` — `number` parsed from
  the string `attributes.chapter` (falls back to the position when null, e.g. one-shots), name from
  `attributes.title`.
- Pages: `GET /at-home/server/<chapter id>` → `let` names `baseUrl` and `chapter.hash`; each page URL is
  `{baseUrl}/data/{hash}/{file}` (`$.chapter.data[*]`).

## Limits

- Licensed chapters (external, e.g. MangaPlus) have no pages on MangaDex: the at-home answer comes back with an
  empty `data` list, so the reader shows no pages for them.
- Units are capped at the first 100 chapters (one request, no pagination in the contract).
- Several scanlations of the same chapter number: only the first is kept (engine rule).
- Rate limit kept at 30 requests/minute per device.
- The at-home image hosts (`*.mangadex.network`) are not in `hosts`: page images are loaded by the app's image
  loader, which doesn't go through the rules engine.

## Checked by hand (2026-10-22)

- Search `title=one piece` with `availableTranslatedLanguage[]=fr`: ids, `ja-ro`-only titles, cover `fileName`s.
- `chapter?manga=…&translatedLanguage[]=fr&order[chapter]=asc`: string chapter numbers, null titles, external
  chapters flagged by `pages: 0`.
- `at-home/server/<chapter id>`: `baseUrl` + `hash` + file list; a built page URL returned HTTP 200.
