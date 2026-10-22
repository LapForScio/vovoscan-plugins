# ManhuaUS

Manga, manhwa and manhua from [ManhuaUS](https://manhuaus.club), a WordPress **Madara** site. Kind: `comic`.

The source reads the site directly: paginated catalog with server-side search, and — instead of the
Ajax chapter endpoint — the **complete chapter list, which Madara embeds as JSON in each title page**
(`script#mk-chapters-data`). Reader images come from the site's own uploads. No key, no account, no
setting to fill.

## Settings

None.

## Structure relied on (checked 2026-10-22, with the engine's User-Agent)

- Catalog: `GET /manga/page/<n>/?s=<search>&post_type=wp-manga` — card grid (`a.acard`), id extracted
  from the card's `href` (`/manga/<slug>/`), cover from the card image, status badge from
  `.ac-status`. `hasNext` from the presence of `a.nextpostslink`.
- Title: `GET /manga/<slug>/` — name (`h1.htitle`), cover (`img.wp-post-image`), description
  (meta), genres (`a.chip`), status (`.htag--status`).
- Units: the whole chapter list is embedded in the title page as JSON inside
  `script#mk-chapters-data` (`$.items[*]`); item id and number are `$.num`, name is `$.name`.
- Chapter: `GET /manga/<slug>/chapter-<num>/` — reader images (`img.wp-manga-chapter-img`); the URL
  falls back from `data-src` to `src` (lazy loading: only the first image has `src` populated).

## Engine features used

- CSS selector + `path` together: an element selected with CSS (here the embedded `<script>`) is
  parsed as JSON and then queried with JSONPath.
- `attrs` fallback on the content item URL (`data-src`, then `src`).
- Server-side search through the `s` query parameter.

**Requires a recent app version** (CSS+JSONPath selector and attribute fallback).

## Limits

- Series ids are opaque Madara slugs (no human-readable mapping).
- `format` is a constant `manhua`; the site mixes manga and manhwa under the same catalog.
- Chapter list order is as embedded by the site (newest first); the engine sorts by number for
  display.
