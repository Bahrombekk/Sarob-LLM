"""Sarob filtrini Open WebUI'ga o'rnatadi: install_filter.py <fayl.py> <id> <nomi>"""
import json, sqlite3, sys, time

fid, name = sys.argv[2], sys.argv[3]
content = open(sys.argv[1], encoding="utf-8").read()
now = int(time.time())
c = sqlite3.connect("/app/backend/data/webui.db")
uid = c.execute("select id from user where role='admin' limit 1").fetchone()[0]
meta = {"description": name, "manifest": {"title": name, "version": "1.0"}}
c.execute("insert into function (id,user_id,name,type,content,meta,created_at,updated_at,valves,is_active,is_global) "
          "values (?,?,?,?,?,?,?,?,?,1,0) on conflict(id) do update set content=excluded.content, name=excluded.name, "
          "meta=excluded.meta, updated_at=excluded.updated_at, is_active=1",
          (fid, uid, name, "filter", content, json.dumps(meta), now, now, "{}"))
c.commit()
print("filtr o'rnatildi:", fid)
