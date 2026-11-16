# 01 · First Push

Your page at `site/index.html` still says **TODO** in three places. Replace them, save the change in git, and upload it to GitHub.

**Words you'll see**
- **commit**: a saved snapshot of your files, with a short message saying what changed.
- **push**: upload your commits to GitHub.
- **remote** / **origin**: the copy of your repo on GitHub. `origin` is just the usual nickname for it.

**Steps**

1. Open `site/index.html` in any editor and replace every `TODO`. Save the file.
2. Save that change in git:
   ```bash
   git status                   # shows site/index.html as "modified"
   git add site/index.html      # pick this file for the next commit
   git commit -m "Fill in my page"
   ```
3. On GitHub, click **+** → **New repository**. Give it any name, make it **Public**, and leave "Add a README" **unticked**, so it starts empty.
4. Connect this folder to that GitHub repo and upload. Replace `<your-username>` and `<repo>` with yours (GitHub shows this URL on the empty repo page):
   ```bash
   git remote add origin https://github.com/<your-username>/<repo>.git
   git push -u origin main
   ```
   Asked for a password? GitHub doesn't accept your account password here. Run `gh auth login` first (GitHub CLI), or use a personal access token as the password.
5. On your repo page open **Actions** → the latest **Check** run → **Summary**. The flag is there once the task is done. If it shows a hint instead, fix that, then `git add`, `git commit` and `git push` again.

`refusing to allow an OAuth App to create or update workflow`? Run `gh auth refresh -s workflow`, then push again.
