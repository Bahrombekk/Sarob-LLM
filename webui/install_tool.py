"""Sarob asbobini Open WebUI bazasiga o'rnatadi.

Ishlatish: install_tool.py <fayl.py> [tool_id] [nomi]
Modellarga biriktirish make_sarob.py dagi toolIds orqali bo'ladi.
"""
import json, sqlite3, sys, time, types

from open_webui.utils.tools import get_tool_specs

TOOL_ID = sys.argv[2] if len(sys.argv) > 2 else "sarob_internet"
NAME = sys.argv[3] if len(sys.argv) > 3 else "Internet (Sarob)"
content = open(sys.argv[1], encoding="utf-8").read()
mod = types.ModuleType(TOOL_ID)
exec(content, mod.__dict__)
specs = get_tool_specs(mod.Tools())
print("funksiyalar:", [s["name"] for s in specs])

now = int(time.time())
c = sqlite3.connect("/app/backend/data/webui.db")
uid = c.execute("select id from user where role='admin' limit 1").fetchone()[0]
meta = {"description": NAME, "manifest": {"title": NAME, "version": "1.0"}}
c.execute(
    "insert into tool (id,user_id,name,content,specs,meta,created_at,updated_at,valves) values (?,?,?,?,?,?,?,?,?) "
    "on conflict(id) do update set name=excluded.name, content=excluded.content, specs=excluded.specs, "
    "meta=excluded.meta, updated_at=excluded.updated_at",
    (TOOL_ID, uid, NAME, content, json.dumps(specs), json.dumps(meta), now, now, "{}"),
)
c.commit()
print(f"o'rnatildi: {TOOL_ID}")
