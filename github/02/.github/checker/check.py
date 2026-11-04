import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import Result, gh_api, is_ancestor, log, main, read_head, reveal  # noqa: E402

TITLE = "Add yourself via branch + pull request"


def branch_and_pr():
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "").lower()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not owner or not repo:
        return [Result(TITLE, False, "Checker must run in GitHub Actions (GITHUB_REPOSITORY not set).")]

    raw = read_head("site/team.json")
    if raw is None:
        return [Result(TITLE, False, "site/team.json is missing on main.")]
    try:
        team = json.loads(raw)
        assert isinstance(team, list)
    except (json.JSONDecodeError, AssertionError) as e:
        return [Result(TITLE, False, f"site/team.json on main is not a valid JSON list ({e}). The PR check would have caught this!")]
    if not any(isinstance(m, dict) and str(m.get("github", "")).lower() == owner for m in team):
        return [Result(TITLE, False, f'No entry with "github": "{owner}" in site/team.json on main yet.')]

    pulls = gh_api(f"/repos/{repo}/pulls?state=closed&base=main&per_page=100")
    if pulls is None:
        return [Result(TITLE, False, "Couldn't reach the GitHub API. Re-run the workflow from the Actions tab.")]
    for pr in pulls:
        sha = pr.get("merge_commit_sha")
        if not pr.get("merged_at") or not sha or not is_ancestor(sha):
            continue
        files = gh_api(f"/repos/{repo}/pulls/{pr['number']}/files") or []
        if any(f.get("filename") == "site/team.json" for f in files):
            if pr.get("head", {}).get("ref") == "main":
                continue
            log.info("found merged PR #%s", pr["number"])
            return [Result(TITLE, True, reveal("ICAgICBWDxsPB04APhMZKwwMARdIMhsLGUgJFR4="))]
    return [Result(TITLE, False,
                   "You're in team.json, but not through a merged pull request. Pushing straight to main "
                   "doesn't count: make a branch, push it, open a PR, wait for the check, then merge.")]


main("02 Branch and PR", [branch_and_pr])
