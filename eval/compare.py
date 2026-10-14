"""Asl Kameralar.xlsx bilan Sarob rasmlardan yaratgan natijani solishtiradi."""
import re
import pandas as pd

asl = pd.read_excel("/workspace/_asl_kameralar.xlsx", sheet_name="Kameralar")
sar = pd.read_excel("/workspace/fayllar/kameralar_sinov.xlsx", sheet_name="Jadval 1")
print("Sarob ustunlari:", list(sar.columns))
sar.columns = ["Holati", "Kamera nomi", "Filial nomi 1", "Filial nomi 2", "Vaqt"][:len(sar.columns)] + list(sar.columns[5:])


def norm(s):
    s = str(s).replace("⭐", "").replace("★", "")
    return re.sub(r"\s+", " ", s).strip().lower()


asl["k"] = asl["Kamera nomi"].map(norm)
sar["k"] = sar["Kamera nomi"].map(norm)
asl_set, sar_set = set(asl["k"]), set(sar["k"])

print(f"Asl: {len(asl)} qator ({asl['k'].nunique()} noyob nom) | Sarob: {len(sar)} qator ({sar['k'].nunique()} noyob nom)")
dup = sar[sar.duplicated("k", keep=False)].sort_values("k")
print(f"\nSarobdagi takroriy nomlar ({dup['k'].nunique()} ta nom, {len(dup) - dup['k'].nunique()} ortiqcha qator):")
print(dup[["Holati", "Kamera nomi", "Vaqt"]].to_string(index=False)[:1500])

missing = sorted(asl_set - sar_set)
extra = sorted(sar_set - asl_set)
print(f"\nAslda bor, Sarobda YO'Q ({len(missing)}): {missing}")
print(f"Sarobda bor, aslda YO'Q ({len(extra)}): {extra}")

m = asl.merge(sar.drop_duplicates("k"), on="k", suffixes=("_asl", "_sar"))
st_ok = (m["Holati_asl"].map(norm) == m["Holati_sar"].map(norm))
org_ok = (m["Tashkilot"].map(norm) == m["Filial nomi 1"].map(norm))
name_exact = (m["Kamera nomi_asl"].map(lambda s: re.sub(r"\s+", " ", str(s)).strip())
              == m["Kamera nomi_sar"].map(lambda s: re.sub(r"\s*⭐\s*", "", re.sub(r"\s+", " ", str(s))).strip()))
print(f"\nMos kelgan kameralar: {len(m)} / {len(asl)} ({len(m) / len(asl):.1%})")
print(f"Nomi harfma-harf to'g'ri: {name_exact.sum()} / {len(m)}")
print(f"Holati (Ulangan/Ulanmagan) bir xil: {st_ok.sum()} / {len(m)}")
print(f"Tashkilot nomi bir xil: {org_ok.sum()} / {len(m)}")
bad = m[~org_ok][["Kamera nomi_asl", "Tashkilot", "Filial nomi 1"]]
if len(bad):
    print("\nTashkilot farqlari:\n" + bad.to_string(index=False)[:1500])
bads = m[~st_ok][["Kamera nomi_asl", "Holati_asl", "Holati_sar", "Oxirgi faollik", "Vaqt"]]
if len(bads):
    print("\nHolat farqlari:\n" + bads.to_string(index=False)[:1500])
