# Changelog

## 1.0.0

- Rolia Scan through the site's own endpoints: catalog search via `POST /wp-json/manga/v1/load`
  (24/page), title page for metadata and the numeric manga id, chapter lists from the signed
  `/auth/manga-chapters` endpoint (md5 time token reproduced with `{{unix}}`, `{{utc:...}}` and the
  `md5` transform), pages from `/auth/chapter-content` (images on roliascan.org).
