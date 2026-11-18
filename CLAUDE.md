# wildrock.build

Static one-page site on GitHub Pages (push to `main` deploys). `index.html` is the source of truth.

- **Spanish page:** `es/index.html` is generated. Never edit it by hand. After any change to `index.html`, run `python3 tools/build_es.py` and commit both files. If English copy changed, the script fails and lists the strings whose translation in `tools/build_es.py` (PAIRS) needs updating.
- **Language choice:** the `<!-- lang-detect -->` script in the head (on both pages) redirects to the language saved in the `wr-lang` cookie, set by the EN/ES toggle. With no cookie, a browser whose primary language is Spanish is sent from `/` to `/es/`.
- Spanish copy uses formal "usted".
