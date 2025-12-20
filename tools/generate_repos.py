import os
import requests

USER = os.getenv("GITHUB_USER", "jessemuldergit")
TOKEN = os.getenv("GITHUB_TOKEN")
INDEX_FILE = "docs/index.md"

EXCLUDE_FORKS = True
EXCLUDE_ARCHIVED = True
MAX_REPOS = 12

def gh_get(url, params=None):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def build_section(repos):
    lines = []
    lines.append("| Repo | Beschrijving | Taal | ⭐ |")
    lines.append("|---|---|---:|---:|")

    for r in repos:
        name = r["name"]
        url = r["html_url"]
        desc = (r.get("description") or "").replace("\n", " ").strip()
        lang = r.get("language") or ""
        stars = r.get("stargazers_count", 0)
        lines.append(f"| [{name}]({url}) | {desc} | {lang} | {stars} |")

    return "\n".join(lines)

def main():
    repos = gh_get(
        f"https://api.github.com/users/{USER}/repos",
        params={"per_page": 100, "sort": "updated"},
    )

    filtered = []
    for r in repos:
        if EXCLUDE_FORKS and r.get("fork"):
            continue
        if EXCLUDE_ARCHIVED and r.get("archived"):
            continue
        filtered.append(r)

    repos = filtered[:MAX_REPOS]

    with open(INDEX_FILE, encoding="utf-8") as f:
        content = f.read()

    start = "<!-- REPOS_START -->"
    end = "<!-- REPOS_END -->"

    if start not in content or end not in content:
        raise RuntimeError("Markers not found in index.md")

    before = content.split(start)[0]
    after = content.split(end)[1]

    section = build_section(repos)

    new_content = (
        before
        + start
        + "\n\n"
        + section
        + "\n\n"
        + end
        + after
    )

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated index.md with {len(repos)} repos")

if __name__ == "__main__":
    main()
