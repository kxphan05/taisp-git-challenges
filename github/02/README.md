# 02 · Branch and Pull Request

Add yourself to `site/team.json` **through a pull request**, not by committing straight to `main`.

**Words you'll see**
- **branch**: a separate line of work. You change things on your branch, and `main` stays untouched until you merge.
- **pull request (PR)**: a request on GitHub to merge your branch into `main`. Teammates (and automatic checks) look at it first.
- **merge**: bring the commits from one branch into another.

**Steps**

1. Make a new **empty public** GitHub repo (like in 01) and upload this folder to it:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo>.git
   git push -u origin main
   ```
2. Make your own branch and switch to it:
   ```bash
   git switch -c add-<your-username>
   ```
3. Open `site/team.json` and add yourself to the list. Note the new comma after the mentor's line: every entry except the last one ends with `,`.
   ```json
   [
     {"name": "TAISP Mentor", "github": "taisp-mentors", "role": "mentor"},
     {"name": "Your Name", "github": "<your-username>", "role": "what you do"}
   ]
   ```
4. Commit it and upload the **branch** (not `main`):
   ```bash
   git add site/team.json
   git commit -m "Add <your-username> to the team"
   git push -u origin add-<your-username>
   ```
5. On GitHub you'll see a **Compare & pull request** button. Open the PR into `main` **of your own repo**.
6. Wait for **PR check** to go green. Red? Click it, read the error, fix the file, then commit and push again on the same branch. The PR updates by itself.
7. Click **Merge pull request**.
8. Open **Actions** → the latest **Check** run → **Summary** for the flag.
