import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import Result, main, participant_commits, read_head, reveal  # noqa: E402


def first_push():
    mine = participant_commits()
    idx = read_head("site/index.html")
    if idx is None:
        return [Result("Fix the page and push", False, "site/index.html is missing. Did you delete it? `git restore site/index.html`")]
    if not mine:
        return [Result("Fix the page and push", False,
                       "No commits from you yet. Edit site/index.html, then run "
                       "`git add site/index.html`, `git commit -m \"Fill in my page\"` and `git push`.")]
    if "TODO" in idx:
        return [Result("Fix the page and push", False,
                       "Your commit arrived, but site/index.html still contains TODO. Replace every TODO, commit, push again.")]
    return [Result("Fix the page and push", True, reveal("ICAgICBWCwAcGlk3ERYYHD4AAC9ZBQwxAUwaBQYYABw="))]


main("01 First Push", [first_push])
