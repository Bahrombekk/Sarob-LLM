"""
title: Bazalar (Sarob)
description: Biznes bazalaridan faqat o'qish rejimida ma'lumot olish (SQL SELECT): SQLite nusxalar va jonli PostgreSQL.
version: 1.1
"""

import json
import os
import re
import sqlite3
import time

BAZALAR = os.environ.get("SAROB_BAZALAR", "/bazalar")          # SQLite nusxalar: <nom>.db
ULANISHLAR = os.environ.get("SAROB_ULANISHLAR", "/run/sarob_pg")  # jonli PostgreSQL: <nom>.dsn (faqat o'qish foydalanuvchisi)
MAX_ROWS = 200
TIMEOUT_SEC = 20


def _sqlite_names():
    return sorted(f[:-3] for f in os.listdir(BAZALAR) if f.endswith(".db")) if os.path.isdir(BAZALAR) else []


def _pg_names():
    return sorted(f[:-4] for f in os.listdir(ULANISHLAR) if f.endswith(".dsn")) if os.path.isdir(ULANISHLAR) else []


def _list():
    return [f"{n} (jonli PostgreSQL)" for n in _pg_names()] + [f"{n} (SQLite nusxa)" for n in _sqlite_names()]


def _kind(baza: str):
    name = re.sub(r"\s*\(.*\)$", "", os.path.basename(baza or "")).removesuffix(".db").removesuffix(".dsn")
    if name in _pg_names():
        return "pg", name
    if name in _sqlite_names():
        return "sqlite", name
    raise FileNotFoundError(f"'{name}' bazasi topilmadi. Mavjudlari: {', '.join(_list()) or 'yoq'}")


def _sqlite(name):
    c = sqlite3.connect(f"file:{os.path.join(BAZALAR, name + '.db')}?mode=ro", uri=True, check_same_thread=False)
    c.execute("pragma query_only = 1")
    deadline = time.time() + TIMEOUT_SEC
    c.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 10000)
    return c


def _pg(name):
    import psycopg2

    dsn = open(os.path.join(ULANISHLAR, name + ".dsn")).read().strip()
    c = psycopg2.connect(dsn, connect_timeout=8,
                         options=f"-c default_transaction_read_only=on -c statement_timeout={TIMEOUT_SEC * 1000}")
    c.set_session(readonly=True, autocommit=True)
    return c


def _run(kind, name, sql):
    if kind == "sqlite":
        cur = _sqlite(name).execute(sql)
        return [d[0] for d in cur.description or []], cur.fetchmany(MAX_ROWS + 1)
    with _pg(name) as c, c.cursor() as cur:
        cur.execute(sql)
        return [d[0] for d in cur.description or []], cur.fetchmany(MAX_ROWS + 1)


class Tools:
    def __init__(self):
        pass

    def bazalar_tuzilishi(self, baza: str = "") -> str:
        """
        Show available business databases, or the structure of one database: tables, columns with types, row counts
        and 2 sample rows per table. ALWAYS call this before writing SQL for a database you have not inspected yet.
        Prefer the live PostgreSQL database for current data; SQLite copies are older snapshots.
        :param baza: Database name (e.g. "kamera_jonli"). Empty = list all databases.
        :return: Database list or schema description.
        """
        if not baza:
            names = _list()
            return "Mavjud bazalar: " + (", ".join(names) if names else "hech qanday baza ulanmagan")
        try:
            kind, name = _kind(baza)
        except Exception as e:
            return f"XATO: {e}"
        out = []
        try:
            if kind == "sqlite":
                c = _sqlite(name)
                for (t,) in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"):
                    cols = [(r[1], r[2] or "?") for r in c.execute(f"pragma table_info('{t}')")]
                    n = c.execute(f'select count(*) from "{t}"').fetchone()[0]
                    sample = c.execute(f'select * from "{t}" limit 2').fetchall()
                    out.append(f"## {t} ({n} qator)\nUstunlar: " + ", ".join(f"{a} {b}" for a, b in cols)
                               + "\nNamuna: " + json.dumps(sample, ensure_ascii=False, default=str)[:600])
            else:
                with _pg(name) as c, c.cursor() as cur:
                    # Faqat ruxsat berilgan ustunlar (maxfiy ustunlar bu foydalanuvchiga ko'rinmaydi)
                    cur.execute("""select p.table_name, p.column_name, c.data_type
                                   from information_schema.column_privileges p
                                   join information_schema.columns c using (table_schema, table_name, column_name)
                                   where p.grantee = current_user and p.privilege_type = 'SELECT' and p.table_schema = 'public'
                                   order by p.table_name, c.ordinal_position""")
                    tables = {}
                    for t, col, typ in cur.fetchall():
                        tables.setdefault(t, []).append((col, typ))
                    for t, cols in tables.items():
                        names = ", ".join(f'"{a}"' for a, _ in cols)
                        cur.execute(f'select count(*) from public."{t}"')
                        n = cur.fetchone()[0]
                        cur.execute(f'select {names} from public."{t}" limit 2')
                        sample = cur.fetchall()
                        out.append(f"## {t} ({n} qator)\nUstunlar: " + ", ".join(f"{a} {b}" for a, b in cols)
                                   + "\nNamuna: " + json.dumps(sample, ensure_ascii=False, default=str)[:600])
                    out.insert(0, "JONLI PostgreSQL. Eslatma: SELECT * ishlamaydi — ustunlarni nomma-nom yoz "
                                  "(faqat yuqoridagi ustunlarga ruxsat bor).")
        except Exception as e:
            return f"XATO: bazaga ulanib bo'lmadi ({str(e)[:200]})."
        return "\n\n".join(out)

    def baza_sorov(self, baza: str, sql: str) -> str:
        """
        Run a READ-ONLY SQL query (SELECT or WITH only) against a business database and return rows.
        Live databases are PostgreSQL (use PostgreSQL syntax: now(), date_trunc, interval '7 days', ILIKE);
        SQLite copies use SQLite syntax. Use aggregation (COUNT, SUM, GROUP BY) instead of fetching many rows.
        Max 200 rows are returned. In PostgreSQL list columns explicitly (SELECT * is not permitted).
        :param baza: Database name from bazalar_tuzilishi (e.g. "kamera_jonli").
        :param sql: A single SELECT/WITH SQL query.
        :return: JSON with columns, rows and row count, or an error to fix the query.
        """
        q = (sql or "").strip().rstrip(";")
        if not re.match(r"(?is)^\s*(select|with)\b", q) or ";" in q:
            return "XATO: faqat bitta SELECT (yoki WITH ... SELECT) so'rovga ruxsat bor."
        try:
            kind, name = _kind(baza)
            cols, rows = _run(kind, name, q)
        except Exception as e:
            return f"XATO: {str(e)[:400]}. So'rovni tuzatib qayta urin (avval bazalar_tuzilishi bilan ustun nomlarini tekshir)."
        more = len(rows) > MAX_ROWS
        rows = rows[:MAX_ROWS]
        return json.dumps({"baza": f"{name} ({'jonli PostgreSQL' if kind == 'pg' else 'SQLite nusxa'})",
                           "ustunlar": cols, "qatorlar": rows, "soni": len(rows),
                           "izoh": "natija 200 qator bilan cheklandi, GROUP BY/LIMIT ishlat" if more else ""},
                          ensure_ascii=False, default=str)
