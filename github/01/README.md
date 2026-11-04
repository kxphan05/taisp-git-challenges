# 01 · First Push

Your page at `site/index.html` still says **TODO** in three places.

1. Fill them in, then `git add`, `git commit` and make sure it is on `main`.
2. On GitHub, create a new **empty public** repo (no README).
3. Push to it:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo>.git
   git push -u origin main
   ```
4. Open your repo → **Actions** → the latest **Check** run → **Summary**. The flag is there once the task is done.

`refusing to allow an OAuth App to create or update workflow`? Run `gh auth refresh -s workflow`, or push over SSH.
