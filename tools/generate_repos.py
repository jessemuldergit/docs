import os
import requests

USER = os.getenv("GITHUB_USER", "jessemuldergit")
TOKEN = os.getenv("GITHUB_TOKEN")  # in Actions beschikbaar
OUTFILE = os.getenv("REPOS_OUTFILE", "docs/repos.md")

EXCLUDE_FORKS = True
EXCLUDE_ARCHIVED = True
MAX_REPOS = 100  # pas aan als je meer hebt

def gh_get(url: str, params=None):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    repos = gh_get(
        f"https://api.github.com/users/{USER}/repos",
        params={"per_page": 100, "sort": "updated", "direction": "desc"},
    )

    filtered = []
    for r in repos:
        if EXCLUDE_FORKS and r.get("fork"):
            continue
        if EXCLUDE_ARCHIVED and r.get("archived"):
            continue
        filtered.append(r)

    filtered = filtered[:MAX_REPOS]

    lines = []
    lines.append(f"# GitHub repos ({USER})")
    lines.append("")
    lines.append("> Deze pagina wordt automatisch gegenereerd bij elke build.")
    lines.append("")
    lines.append("| Repo | Beschrijving | Taal | ⭐ | Laatst bijgewerkt |")
    lines.append("|---|---|---:|---:|---:|")

    for r in filtered:
        name = r["name"]
        url = r["html_url"]
        desc = (r.get("description") or "").replace("\n", " ").strip()
        lang = r.get("language") or ""
        stars = r.get("stargazers_count", 0)
        updated = (r.get("updated_at") or "")[:10]  # YYYY-MM-DD
        lines.append(f"| [{name}]({url}) | {desc} | {lang} | {stars} | {updated} |")

    os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {OUTFILE} with {len(filtered)} repos")

if __name__ == "__main__":
    main()
