# Rolia Scan

Manhwa and manga from [Rolia Scan](https://roliascan.com). Kind: `comic`.

The source uses the **site's own endpoints**, the same ones its web reader calls: the browse/search
endpoint is a `POST` on the WordPress REST API, chapter lists come from a signed endpoint
(`/auth/manga-chapters`) that expects a time-based md5 token computed exactly like the site's
JavaScript does, and pages come from the site's storage (served under `roliascan.org`).
No key, no account, no setting to fill.

## Settings

None.

## Structure relied on (checked 2026-10-22, with the engine's User-Agent)

- Catalog: `POST /wp-json/manga/v1/load` with JSON body `{"page": N, "search": "..."}` — returns a
  flat JSON array (24 items per page, no total count). The item id is extracted from the series URL
  (`/manga/<slug>/`); `hasNext` is inferred from a 24th item being present.
- Title: `GET /manga/<slug>/` — HTML page carrying the numeric `data-manga-id` used by the signed
  endpoint (`let` captures it as `mid`), plus name, cover, description and genres.
- Units: `GET /auth/manga-chapters` with `manga_id=<mid>&offset=0&limit=500&order=asc` and the signed
  query `_t = md5("<unix>mng_ch_<utc yyyyMMddHH>")` truncated to 16 chars, `_ts = <unix>`. Chapter
  id is the site's own chapter id; `number` is the chapter number.
- Chapter: `GET /auth/chapter-content?chapter_id=<id>` — `$.images[*]` page URLs on `roliascan.org`.

## Engine features used

- `method: "post"` with a JSON body (`contentType: "application/json"`).
- Built-in placeholders `{{unix}}` and `{{utc:yyyyMMddHH}}`, and the `md5` transform, to reproduce
  the site's signed query token.
- `title.let` to capture the numeric manga id (`mid`) from the title page and reuse it in the units
  request.
- `query` values as rule objects (template + transforms) instead of plain strings.

**Requires a recent app version** (POST requests, clock/md5 placeholders, `title.let`).

## Limits

- The catalog endpoint returns 24 items per page and no total count; `hasNext` is a heuristic (a
  full 24th page means "probably more"). The last page is simply short or empty.
- Chapter lists are capped at 500 chapters per series (well above anything currently published).
- `status` on the catalog item is cosmetic; the title page does not expose a reliable status, so the
  title field is a constant `ongoing`.
