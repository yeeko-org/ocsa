"""Aplica la regla de nombres de Ricardo (09/11/2026) al JSON del INPI."""
import json, sys, unicodedata
from pathlib import Path

PATH = Path(sys.argv[1])
APOS = str.maketrans({c: "'" for c in "’‘´`ʾʼ"})
# Autodenominación elegida; None = sin paréntesis.
CHOSEN = {
    "Amuzgo": "Ñomndaa", "Chichimeco": "Éza'r", "Chinanteco": "Tsa köwï",
    "Ch'ol": None, "Cucapá": None, "Cuicateco": "Ñoo Dibaku",
    "Guarijío": "Makurawe", "Huasteco": "Téenek", "Mazahua": "Jñatjo",
    "Mixe": "Ayuuk", "Mixteco": "Ñuu Savi", "Otomí": "Hñähñu",
    "Pima": "O'oba", "Popoluca de la Sierra": "Nuntajɨɨyi",
    "Tarahumara": "Rarámuri", "Tepehuano del Sur": "O'dam",
    "Totonaco": "Tutunakú", "Zapoteco": "Binnizá", "Zoque": "Angpøn",
    # Variantes ortográficas de la misma palabra no llevan paréntesis;
    # Jakalteko toma Popti'. Confirmado por Ricardo el 09/11/2026.
    "Kaqchikel": None, "K'iche'": None, "Q'eqchi'": None,
    "Jakalteko": "Popti'", "Pame": "Xi'iuy", "Seri": "Comca'ac",
    # Ricardo, 09/11/2026: el DOF solo, aunque la autodenominación difiera.
    "Q'anjob'al": None, "Tacuate": None,
    # Ricardo, 09/11/2026: la autodenominación sola (ver ALONE).
    "Paipai": "Pa ipai", "Tojolabal": "Tojol-ab'al",
}
# Nombre = la autodenominación sin paréntesis: es variante de grafía del DOF
# y la regla general la descartaría. Tojol-ab'al va sin el espacio que el DOF
# imprime antes del guion; la forma literal queda en los alternativos.
ALONE = {"Paipai", "Tojolabal"}
SPANISH = {"ñ", "Ñ"}

def apos(t): return t.translate(APOS).replace("¨", "'").strip()

def key(t):
    t = unicodedata.normalize("NFKD", apos(t).casefold())
    return "".join(c for c in t if not unicodedata.combining(c)
                   and c not in "' -")

def fold(t):
    """Sin apóstrofos ni diacríticos, salvo la ñ."""
    out = []
    for ch in apos(t).replace("'", ""):
        if ch in SPANISH: out.append(ch); continue
        d = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in d if not unicodedata.combining(c))
        out.append({"ɨ": "i", "ø": "o"}.get(base, base))
    return "".join(out)

data = json.loads(PATH.read_text(encoding="utf-8"))
rows = []
for p in data["pueblos"]:
    dof = p["dof_name"]
    selfs = [apos(s) for s in p["source_alternatives"]]
    if dof in CHOSEN:
        autonym = CHOSEN[dof]
    elif len(selfs) == 1 and p["self_designation"] != dof:
        autonym = selfs[0]
    elif not selfs:
        autonym = None
    else:
        autonym = apos(p["self_designation"])
    if autonym and key(autonym) == key(dof) and dof not in ALONE:
        autonym = None
    if dof in ALONE:
        name = autonym
    else:
        name = f"{autonym} ({dof})" if autonym else dof
    forms = [autonym, dof] + selfs + [apos(s) for s in p["extra_variants"]]
    forms = [f for f in forms if f]
    forms += [fold(f) for f in forms]
    seen, alts = {name.casefold()}, []
    for f in forms:
        if f.casefold() not in seen:
            seen.add(f.casefold()); alts.append(f)
    p["name"] = name
    p["autonym"] = autonym
    p["alternative_names"] = alts
    rows.append((p["no"], dof, name))
data["fields"]["name"] = (
    "Nombre en OCSA: «Autodenominación (Denominación DOF)» cuando difieren, "
    "la denominación del DOF sola cuando coinciden; apóstrofo recto. Regla "
    "de Ricardo del 09/11/2026, con cuatro excepciones suyas del mismo día: "
    "Pa ipai y Tojol-ab'al llevan la autodenominación sola; Q'anjob'al y "
    "Tacuate, la denominación del DOF sola")
data["fields"]["autonym"] = (
    "Autodenominación elegida para el nombre; null cuando el nombre es la "
    "denominación del DOF sola")
data["fields"]["alternative_names"] = (
    "Todas las demás formas: autodenominación y denominación del DOF sueltas, "
    "las del DOF y el micrositio, las grafías de prensa y su forma sin "
    "apóstrofos ni diacríticos (salvo la ñ)")
order = list(data["pueblos"][0].keys())
PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8")
for r in rows: print(*r, sep=" | ")
