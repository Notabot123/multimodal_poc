import os, json
DB_FILE = "db.json"

if os.getenv("LOAD_PREBUILT_DB") == "true" and os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        db = json.load(f)
else:
    db = []