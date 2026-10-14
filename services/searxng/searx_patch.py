"""SearXNG'ga qo'shimcha qidiruv tizimlarini qo'shadi va bloklash vaqtlarini qisqartiradi."""
p = "/home/dasuty/sarob/searxng/settings.yml"
s = open(p).read()
extra = """  - name: startpage
    disabled: false
  - name: qwant
    disabled: false
  - name: mojeek
    disabled: false
  - name: yahoo
    disabled: false
  - name: bing news
    disabled: false
  - name: yahoo news
    disabled: false
"""
if "name: startpage" not in s:
    s = s.rstrip() + "\n" + extra
# Bloklangan tizim tezroq qayta ishlatilsin (standart: soatlab)
if "suspended_times" not in s:
    s = s.replace("search:\n", "search:\n  suspended_times:\n    SearxEngineAccessDenied: 600\n"
                  "    SearxEngineCaptcha: 1800\n    SearxEngineTooManyRequests: 600\n"
                  "    cf_SearxEngineCaptcha: 1800\n    cf_SearxEngineAccessDenied: 600\n"
                  "    recaptcha_SearxEngineCaptcha: 1800\n", 1)
open(p, "w").write(s)
print("ok")
