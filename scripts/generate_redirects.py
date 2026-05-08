import re
from pathlib import Path

redirects = []
for path in Path("content/posts").rglob("*.md"):
    if path.name == "_index.md":
        continue
    elif path.name == "index.md":
        raw_slug = path.parent.name
    else:
        raw_slug = path.stem

    match = re.match(r"^\d{4}-\d{2}-\d{2}[-_](.+)$", raw_slug)
    if match:
        slug = match.group(1)
    else:
        slug = raw_slug

    redirects.append(f"/{slug}/ /posts/{slug}/ 301")
Path("static/_redirects").write_text("\n".join(sorted(set(redirects))) + "\n")

print("Generated redirects.")
