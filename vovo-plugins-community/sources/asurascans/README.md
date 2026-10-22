# Asura Scans

Manhwa, manga and manhua from [Asura Scans](https://asurascans.com). Kind: `comic`.

The source reads the **site's own JSON API** (`api.asurascans.com`), the same one its web reader calls:
catalog search and browsing, series metadata, chapter lists and page URLs. Page images are served by
`cdn.asurascans.com`. No key, no account, no setting to fill.

## Settings

None.

## Structure relied on (checked 2026-10-22, with the engine's User-Agent)

- Catalog: `GET /api/series?search=&offset=` — 20 per page (`meta.has_more`, `meta.total`). The item id is
  the series slug (the API accepts it with or without the public URL's hash suffix).
- Title: `GET /api/series/<slug>` — `$.series` (title, author, HTML description stripped of tags, cover,
  genres, status, type).
- Units: `GET /api/series/<slug>/chapters` — `$.data[*].number`; the id is the chapter number, used
  directly in the content URL.
- Chapter: `GET /api/series/<slug>/chapters/<number>` — `$.data.chapter.pages[*].url` on the CDN.

## Engine features used

- `type: "json"` with JSONPath, `let`-free.
- `startIndex` pagination on `offset` (base 0).
- Boolean `hasNext` straight from `$.meta.has_more`.

## Limits

- **Premium / early-access chapters answer without a `pages` list** (`is_locked: true`) until the site's
  unlock time; the reader shows them empty. Free chapters work fully.
- Genres exist on the series but are not exposed as app categories yet.
- Decimals in chapter numbers (e.g. `35.5`) have not been observed; if they appear, the units id is the
  raw number as sent by the API.
