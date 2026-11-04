import json, sys
path = "site/team.json"
try:
    team = json.load(open(path))
except json.JSONDecodeError as e:
    sys.exit(f"::error file={path},line={e.lineno}::team.json is not valid JSON: {e.msg}. (Trailing comma?)")
if not isinstance(team, list):
    sys.exit(f"::error file={path}::team.json must be a JSON list [ ... ]")
seen = set()
for i, m in enumerate(team):
    for key in ("name", "github", "role"):
        if not isinstance(m, dict) or not str(m.get(key, "")).strip():
            sys.exit(f"::error file={path}::entry {i} needs non-empty \"{key}\"")
    if m["github"].lower() in seen:
        sys.exit(f"::error file={path}::duplicate github {m['github']}")
    seen.add(m["github"].lower())
print(f"team.json OK: {len(team)} members")
