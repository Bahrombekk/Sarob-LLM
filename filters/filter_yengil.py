"""
title: Yengil suhbat
description: Uzun suhbatlarni tezlashtiradi: eski xabarlardagi rasmlarni va katta asbob natijalarini modelga qayta yubormaydi. Chatdagi tugma bilan yoqiladi.
version: 1.0
"""

from pydantic import BaseModel, Field

ICON = ("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmls"
        "bD0ibm9uZSIgc3Ryb2tlPSJjdXJyZW50Q29sb3IiIHN0cm9rZS13aWR0aD0iMS44IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1s"
        "aW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xMyAyIDMgMTRoOWwtMSA4IDEwLTEyaC05bDEtOHoiLz48L3N2Zz4=")  # chaqmoq belgisi


class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=-10, description="Boshqa filtrlardan oldin ishlaydi")
        rasm_turlar: int = Field(default=1, description="Oxirgi nechta savolning rasmlari saqlanadi")
        asbob_belgi: int = Field(default=1500, description="Eski asbob natijalaridan qoldiriladigan belgilar soni")

    def __init__(self):
        self.toggle = True  # chatda tugma: faqat foydalanuvchi yoqqanda ishlaydi
        self.icon = ICON
        self.valves = self.Valves()

    def request(self, body: dict, __user__: dict = None) -> dict:
        try:
            msgs = body.get("messages") or []

            def is_real_user(m):
                # Open WebUI asbob natijasidagi rasmlarni "user" xabari sifatida qo'shadi — bu haqiqiy savol emas
                if m.get("role") != "user":
                    return False
                c = m.get("content")
                text = " ".join(p.get("text", "") for p in c if isinstance(p, dict)) if isinstance(c, list) else str(c or "")
                return "images from the tool results above" not in text

            user_idx = [i for i, m in enumerate(msgs) if is_real_user(m)]
            if len(user_idx) < 2:
                return body
            keep_from_img = user_idx[-self.valves.rasm_turlar] if self.valves.rasm_turlar > 0 else len(msgs)
            last_user = user_idx[-1]
            dropped_img, trimmed = 0, 0
            for i, m in enumerate(msgs):
                c = m.get("content")
                # 1) Eski xabarlardagi rasmlar -> qisqa matnli belgi
                if i < keep_from_img and isinstance(c, list):
                    new = []
                    for p in c:
                        if isinstance(p, dict) and p.get("type") == "image_url":
                            dropped_img += 1
                            continue
                        new.append(p)
                    if len(new) != len(c):
                        new.append({"type": "text", "text": "[Bu xabardagi rasm(lar) avval ko'rib chiqilgan; tejash uchun qayta yuborilmadi]"})
                        m["content"] = new
                # 2) Oxirgi savoldan oldingi katta asbob natijalari -> qisqartiriladi
                if i < last_user and m.get("role") == "tool" and isinstance(c, str) and len(c) > self.valves.asbob_belgi:
                    m["content"] = c[: self.valves.asbob_belgi] + f"\n[... eski asbob natijasi qisqartirildi, jami {len(c)} belgi edi]"
                    trimmed += 1
            body["messages"] = msgs
        except Exception:
            pass
        return body
