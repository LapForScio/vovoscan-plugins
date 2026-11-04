# Changelog

## 1.1.0

- Add `laiond.com` (the chapter image host) to `hosts`: the engine's destination guard rejects
  chapter images otherwise (`SourceRejected: address not allowed`), even though the site itself
  hotlink-friendly serves them.

## 1.0.0

- Kingdom (single-series site): the catalog is the series itself (h1, meta description, cover from
  the homepage), all chapters (~890, parsed from `kingdom-chapter-<n>` slugs) as units, reader pages
  from `laiond.com` images on each chapter page.
