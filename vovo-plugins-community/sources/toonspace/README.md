# ToonSpace (toon.free)

Manga, manhwa, manhua and romance webtoons from toon.free ("ToonSpace", Next.js app with a JSON
catalog API). Kind: `comic` (chapter pages as images).

`robots.txt` allows everything except `/*?tab=*` (never used here); catalog and pages are read at
the manifest rate limit, no protection is bypassed, and page images on `i1.toonspace.pics` answer a
plain GET with no Referer.

## Settings

None.

## Limits of this source

- **No search**: the site searches client-side only, so the catalog request ignores `{{search}}`;
  searching in the app shows the browse catalog.
- The explore API mixes in some video "shorts" items: those titles open with an empty chapter
  list (their content is not comics).
- The catalog is a cursor-paginated API (`/api/explore`, opaque `nextCursor`); the app engine
  must support `cursor` pagination.

## Structure relied on (checked 2026-10-21)

- Catalog: `GET /api/explore` → `{"items": [{"slug","title","coverUrl",…}], "nextCursor": …}`;
  next pages repeat with `?cursor=<nextCursor>`.
- Title: `/title/<slug>` — `h1`, authors `h1 + p` ("by …"), synopsis `p.line-clamp-3`, genre
  chips `div.flex.flex-wrap.gap-2 a[href^="/shelf/"]`, status badge
  `span:matches(^(Ongoing|Completed)$)`, chapters `a[href^="/read/"]` (`/read/<slug>/chapter-<n>`).
- Chapter: `/read/<slug>/chapter-<n>` — pages `img[src*="/pages/"]` on `i1.toonspace.pics`.
