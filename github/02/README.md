# 02 · Branch and Pull Request

Add yourself to `site/team.json` **through a pull request**, not by committing to `main`.

1. Push this repo to a new **empty public** GitHub repo of yours:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo>.git
   git push -u origin main
   ```
2. Make a branch, edit `site/team.json` (add `{"name": "...", "github": "<your-username>", "role": "..."}`), commit, and push the branch:
   ```bash
   git switch -c add-<your-username>
   git push -u origin add-<your-username>
   ```
3. On GitHub open a PR **into `main` of your own repo**. Wait for **PR check** to go green (red? read the error, fix, push again), then merge it.
4. Open **Actions** → the latest **Check** run → **Summary** for the flag.
