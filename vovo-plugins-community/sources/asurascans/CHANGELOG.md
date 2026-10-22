# Changelog

## 1.0.0

- Asura Scans through its own JSON API: catalog (`/api/series`, 20/page, `offset` pagination, server-side
  `search`), title metadata (`/api/series/<slug>`), chapter lists (`/api/series/<slug>/chapters`), page
  URLs (`/api/series/<slug>/chapters/<number>` → CDN webp images).
