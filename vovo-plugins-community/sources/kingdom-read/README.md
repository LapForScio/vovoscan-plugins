# Kingdom Read

Kingdom (Yasuhisa Hara) English scans on kingdom-read.online. The site covers this single series: the
catalog is the series itself, and every chapter is linked from the one-page homepage.

## Settings

None.

## Structure relied on (checked 2026-10-22, with the engine's User-Agent)

- Catalog/title: `/` — `h1` ("Kingdom"), description in `meta[name=description]`, cover is the only
  content `<img>` under `wp-content/uploads`. One catalog item (`id` = `kingdom`).
- Units: all ~890 chapter links `a[href*="/comic/kingdom-chapter-"]` on the same page; the id is the
  chapter slug, the number is parsed from `chapter-<n>`. The site lists one duplicate (`…-887-2`);
  the engine keeps the first of two equal numbers.
- Chapter: `/comic/kingdom-chapter-<n>/` — pages are `<img lazyload src="https://laiond.com/…">`
  (18–57 per chapter), hotlink-friendly (plain GET, no Referer).

## Limits

- Single series: search always returns the one item; there are no categories.
- Chapter parts sharing a number (e.g. `887` and `887-2`) collapse to the first.
- Images live on `laiond.com`; the engine's rules never call it (allowed hosts only gate the app's
  own requests), and the app image loader fetches it with a plain GET.
