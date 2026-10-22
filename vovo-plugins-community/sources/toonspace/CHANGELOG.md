# Changelog

## 1.0.0

First draft.

- Catalog from the JSON explore API (`/api/explore`) with `cursor` pagination.
- Titles from `/title/<slug>`, chapter pages from `/read/<slug>/chapter-<n>`.
- No server-side search (the site searches client-side); video "shorts" items appear with an
  empty chapter list.
