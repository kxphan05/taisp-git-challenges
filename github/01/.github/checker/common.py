"""Shared helpers for TAISP git challenge checkers.

Runs inside GitHub Actions (or locally for smoke tests). Stdlib only.
The checker NEVER fails the workflow: it always builds _site/ so the
participant sees hints on their Pages site instead of a red X.
"""
from __future__ import annotations

import base64
import html
import json
import logging
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

MENTOR_EMAIL = "mentor@taisp.invalid"
BOT_EMAIL = "teammate-bot@taisp.invalid"
REPO_ROOT = Path(os.environ.get("TAISP_REPO_ROOT", ".")).resolve()
SITE_SRC = REPO_ROOT / "site"
SITE_OUT = REPO_ROOT / "_site"
PLACEHOLDER = "<!-- CTF_RESULT -->"

logging.basicConfig(
    level=os.environ.get("TAISP_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s checker: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("checker")


# --- flags (light obfuscation only: honour system) -----------------------
_KEY = b"taisp-mini-hack"


def reveal(blob: str) -> str:
    raw = base64.b64decode(blob)
    return bytes(b ^ _KEY[i % len(_KEY)] for i, b in enumerate(raw)).decode()


def hide(flag: str) -> str:  # used by build.py
    raw = flag.encode()
    return base64.b64encode(bytes(b ^ _KEY[i % len(_KEY)] for i, b in enumerate(raw))).decode()


# --- git -----------------------------------------------------------------
class GitError(RuntimeError):
    pass


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True,
    )
    log.debug("git %s -> rc=%s", " ".join(args), proc.returncode)
    if check and proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def is_ancestor(a: str, b: str = "HEAD") -> bool:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", a, b],
        capture_output=True,
    ).returncode == 0


@dataclass
class Commit:
    sha: str
    author_email: str
    author_ts: int
    committer_ts: int
    subject: str
    parents: list[str]


def history(rev: str = "HEAD") -> list[Commit]:
    """All commits reachable from rev, newest first."""
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "log", rev, "--format=%H%x1f%ae%x1f%at%x1f%ct%x1f%s%x1f%P%x1e"],
                         capture_output=True, text=True, check=True).stdout  # unstripped: git() strip() would also eat \x1f
    commits = []
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")  # NOT .strip(): Python treats \x1f as whitespace and would eat empty %P
        if not rec:
            continue
        sha, ae, at, ct, subj, parents = rec.split("\x1f")
        commits.append(Commit(sha, ae.lower(), int(at), int(ct), subj, parents.split()))
    return commits


def find_by_subject(subject: str, email: str = MENTOR_EMAIL, rev: str = "HEAD") -> Commit | None:
    for c in history(rev):
        if c.subject == subject and c.author_email == email:
            return c
    return None


def participant_commits(rev: str = "HEAD") -> list[Commit]:
    return [c for c in history(rev) if c.author_email not in (MENTOR_EMAIL, BOT_EMAIL)]


def read_head(path: str) -> str | None:
    """File content at HEAD (None if not tracked)."""
    try:
        return git("show", f"HEAD:{path}")
    except GitError:
        return None


CONFLICT_MARKERS = ("<<<<<<<", ">>>>>>>")


def has_conflict_markers(text: str) -> bool:
    return any(line.startswith(CONFLICT_MARKERS) or line.strip() == "=======" for line in text.splitlines())


# --- GitHub API (with a fake for local smoke tests) ------------------------
def gh_api(path: str):
    fake_dir = os.environ.get("TAISP_FAKE_API_DIR")
    if fake_dir:
        f = Path(fake_dir) / (path.strip("/").replace("/", "__").split("?")[0] + ".json")
        log.info("fake api %s -> %s", path, f.name)
        return json.loads(f.read_text()) if f.exists() else []
    token = os.environ.get("GITHUB_TOKEN")
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    req = urllib.request.Request(f"{api}{path}", headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        log.error("GitHub API %s failed: %s", path, e)
        return None


# --- results + rendering ---------------------------------------------------
@dataclass
class Result:
    title: str
    passed: bool
    detail: str  # flag if passed, else a hint


def render(challenge_title: str, results: list[Result]) -> None:
    if SITE_OUT.exists():
        shutil.rmtree(SITE_OUT)
    if SITE_SRC.is_dir():
        shutil.copytree(SITE_SRC, SITE_OUT)
    else:
        log.warning("site/ missing; deploying a results-only page")
        SITE_OUT.mkdir()
        (SITE_OUT / "index.html").write_text(f"<!doctype html><title>{challenge_title}</title><body>{PLACEHOLDER}</body>")

    rows = []
    for r in results:
        icon = "&#x2705;" if r.passed else "&#x274C;"
        body = (f"<code class='flag'>{html.escape(r.detail)}</code>" if r.passed
                else f"<span class='hint'>{html.escape(r.detail)}</span>")
        rows.append(f"<li>{icon} <b>{html.escape(r.title)}</b><br>{body}</li>")
    panel = (
        "<section id='ctf-result' style='font-family:system-ui;border:2px dashed #888;"
        "padding:1rem;margin:1.5rem 0;border-radius:8px'>"
        f"<h2 style='margin-top:0'>CTF checker: {html.escape(challenge_title)}</h2>"
        f"<ul style='line-height:1.6'>{''.join(rows)}</ul>"
        "<small>Re-checked on every push to main. Paste flags into CTFd.</small></section>"
    )
    index = SITE_OUT / "index.html"
    page = index.read_text() if index.exists() else "<!doctype html><body></body>"
    if PLACEHOLDER in page:
        page = page.replace(PLACEHOLDER, panel, 1)
    elif "</body>" in page:
        page = page.replace("</body>", panel + "</body>", 1)
    else:
        page += panel
    index.write_text(page)

    passed = sum(r.passed for r in results)
    log.info("%s: %d/%d checks passed", challenge_title, passed, len(results))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write(f"## {challenge_title}: {passed}/{len(results)} done\n\n")
            for r in results:
                # the run summary is where the flag is shown (no Pages site in this format)
                fh.write(f"- {'✅' if r.passed else '❌'} **{r.title}**: {r.detail}\n")


def main(challenge_title: str, checks) -> None:
    """Run each check; a crashing check becomes a hint, never a failed job."""
    results: list[Result] = []
    for check in checks:
        try:
            results.extend(check())
        except Exception as e:  # noqa: BLE001 - surface any failure as a hint
            log.exception("check %s crashed", check.__name__)
            results.append(Result(check.__name__, False, f"Checker error ({e}). Ask a mentor."))
    render(challenge_title, results)
    if os.environ.get("TAISP_PRINT_RESULTS"):
        print(json.dumps([r.__dict__ for r in results]))
