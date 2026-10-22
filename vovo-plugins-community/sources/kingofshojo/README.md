# Kingofshojo

Shoujo / romance / fantasy manhwa & manga from kingofshojo.com (WordPress "MangaReader" theme).
Kind: `comic` (chapter pages as images).

The site's `robots.txt` is the permissive WordPress default; the source stays within the manifest
rate limit and reads only public catalog/title/chapter pages (no protection bypassed; chapter
images on `cdn.kingofshojo.com` answer a plain GET with no Referer).

## Settings

None.

## Structure relied on (checked 2026-10-21)

- Catalog/search: `/page/<n>/?s=<query>` (empty `s` = all series, ~490 pages of 10), cards `div.bsx`,
  next page `.pagination a.next`.
- Title: `/manga/<slug>/` — `h1.entry-title`, `div.entry-content-single`, cover `div.thumb img`,
  genres `div.seriestugenre a`, status `td:matches(^Status$) + td`, chapters `#chapterlist li`
  (`data-num`, link `<slug>-chapter-<n>`).
- Chapter: `/<slug>-chapter-<n>/` — pages `#readerarea img` on `cdn.kingofshojo.com`.
