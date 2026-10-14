"""kamera-xarita bazasidan Sarob uchun maxfiy ma'lumotlarsiz nusxa yaratadi (asl fayl o'zgarmaydi)."""
import sqlite3, sys

SRC, DST = sys.argv[1], sys.argv[2]
DROP_TABLES = {"admins", "sessions"}                       # parol xeshlari, sessiya tokenlari
DROP_COLUMNS = {"cameras": {"username", "password_enc", "stream_url"}}  # kamera login/parollari

src = sqlite3.connect(f"file:{SRC}?mode=ro", uri=True)
dst = sqlite3.connect(DST)
for (name,) in src.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'"):
    if name in DROP_TABLES:
        continue
    cols = [r[1] for r in src.execute(f"pragma table_info('{name}')") if r[1] not in DROP_COLUMNS.get(name, set())]
    col_sql = ", ".join(f'"{c}"' for c in cols)
    dst.execute(f'create table "{name}" ({col_sql})')
    rows = src.execute(f'select {col_sql} from "{name}"')
    dst.executemany(f'insert into "{name}" values ({",".join("?" * len(cols))})', rows)
    print(f"{name}: {len(cols)} ustun")
dst.commit()
dst.execute("vacuum")
dst.close()
print("tayyor:", DST)
