# wildrock.build

Static one-page site on GitHub Pages (push to `main` deploys). `index.html` is the source of truth.

- **Spanish page:** `es/index.html` is generated. Never edit it by hand. After any change to `index.html`, run `python3 tools/build_es.py` and commit both files. If English copy changed, the script fails and lists the strings whose translation in `tools/build_es.py` (PAIRS) needs updating.
- **Language detection:** the `<!-- lang-detect -->` block in `index.html` sends visitors whose browser's primary language is Spanish to `/es/`, unless they've chosen a language with the EN/ES toggle (stored in localStorage `wr-lang`). The build strips the block from the Spanish page.
- Spanish copy uses formal "usted".
