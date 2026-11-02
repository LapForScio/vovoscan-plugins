# Changelog

## 1.1.0

- Premium / early-access chapters (`is_premium: true`) are no longer listed: the API serves them without
  pages until the site's own unlock time, which left the reader on an empty chapter. Filtered with
  `units.where` + the `not` transform.

## 1.0.0

- Asura Scans through its own JSON API: catalog (`/api/series`, 20/page, `offset` pagination, server-side
  `search`), title metadata (`/api/series/<slug>`), chapter lists (`/api/series/<slug>/chapters`), page
  URLs (`/api/series/<slug>/chapters/<number>` → CDN webp images).
