import re
from collections import Counter

STRONG_VERBS = {"led","built","launched","increased","reduced","optimized","designed","implemented","drove","managed"}
STOP = set("a an the and or for to of in with on at by from as is are be this that".split())

def tokenize(txt):
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]+", txt.lower())
    return [w for w in words if w not in STOP and len(w)>2]

def job_keywords(job_text, top=40):
    toks = tokenize(job_text)
    freq = Counter(toks)
    return set([w for w,_ in freq.most_common(top)])

def score_bullet(bullet, kw):
    toks = set(tokenize(bullet))
    verb_bonus = 1 if next((v for v in STRONG_VERBS if bullet.lower().startswith(v)), None) else 0
    metric_bonus = 2 if any(ch.isdigit() for ch in bullet) or "%" in bullet else 0
    overlap = len(toks & kw)
    return overlap*2 + verb_bonus + metric_bonus

def suggest_rewrite(bullet, kw):
    toks = set(tokenize(bullet))
    missing = [k for k in kw if k not in toks][:2]
    if not missing: return bullet
    base = bullet.rstrip(".")
    return f"{base} leveraging {', '.join(missing)}."
