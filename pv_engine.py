"""Grading and rules engine for PV Case Lab.

All scores and deadlines come from programmed rules, never from AI.
Each grader returns: {"pts", "max", "notes": [(ok, text)], "critical": bool}
"""

import datetime as dt

from pv_data import CASES, CODING_RULES, CRITERIA, ELEMENTS, NJ_PTS, RULES, STAGES

CASE = {c["id"]: c for c in CASES}
RULE = {r["id"]: r for r in RULES}
LBL = {"y": "Yes", "n": "No", "d": "Don't know"}
PASS_MARK = 75
CAP = 74  # a critical error caps the score below the pass mark


def fmt(d):
    return d.strftime("%d %b %Y")


def day(iso):
    return dt.date.fromisoformat(iso)


def nj_total(answers):
    total = 0
    for i, a in enumerate(answers):
        if a == "y":
            total += NJ_PTS[i][0]
        elif a == "n":
            total += NJ_PTS[i][1]
    return total


def nj_cat(total):
    return "Definite" if total >= 9 else "Probable" if total >= 5 else "Possible" if total >= 1 else "Doubtful"


def result(pts, mx, notes, critical=False):
    return {"pts": round(pts, 1), "max": mx, "notes": notes, "critical": critical}


def stages_for(case):
    wanted = case.get("stages")
    return [s for s in STAGES if wanted is None or s[0] in wanted]


def grade_validity(c, a):
    notes, pts = [], 0
    for key, label in ELEMENTS:
        truth, why = c["elements"][key]
        ok = a["el"][key] == truth
        pts += 2 * ok
        notes.append((ok, f"{label}: {'present' if truth else 'missing'}. {why}"))
    valid = all(v[0] for v in c["elements"].values())
    ok = a["overall"] == ("Valid ICSR" if valid else "Not a valid ICSR (yet)")
    pts += 3 * ok
    notes.append((ok, "Overall: valid, all four minimum elements are present." if valid
                  else "Overall: not valid yet, a minimum element is missing."))
    if c["followups"]:
        useful = [i for i, f in enumerate(c["followups"]) if f["useful"]]
        good = sum(i in useful for i in a["fu"])
        bad = len(a["fu"]) - good
        share = max(0, min(1, (good - bad) / min(3, len(useful))))
        pts += 4 * share
        notes.append((share == 1, f"Follow-up questions: {good} useful, {bad} not useful. Good questions ask for missing "
                                   "clinical facts. They never request unnecessary personal data, give medical advice "
                                   "or ask for a rechallenge."))
    else:
        ok = a["action"] == c["action"]
        pts += 4 * ok
        notes.append((ok, c["action_note"]))
    return result(pts, 15, notes)


def grade_coding(c, a):
    cd = c["code"]
    ok1 = a["pt"] == cd["pt"]
    ok2 = a["rule"] == CODING_RULES[1]
    return result(7 * ok1 + 3 * ok2, 10, [
        (ok1, f"Best term: {cd['pt']}. {cd['why']}"),
        (ok2, "Code what the reporter said and do not add an unsupported diagnosis."),
    ])


def grade_seriousness(c, a):
    pts, notes = 0, []
    for key, label, _ in CRITERIA:
        if key in c["flex"]:
            pts += 2
            continue
        want, got = key in c["ser"], key in a["crit"]
        pts += 2 * (want == got)
        if want != got:
            notes.append((False, f"{label}: {'applies' if want else 'does not apply'} in this case."))
    serious = bool(c["ser"])
    ok = (a["serious"] == "Serious") == serious
    pts += 3 * ok
    notes.insert(0, (ok, f"Overall: {'serious' if serious else 'non-serious'}. {c['ser_note']}"))
    return result(pts, 15, notes, critical=not ok)


def grade_causality(c, a):
    pts, notes = 0, []
    for i, (want, got) in enumerate(zip(c["nj"], a["nj"])):
        if want == got:
            pts += 1
        else:
            notes.append((False, f"Naranjo question {i + 1}: expected {LBL[want]}, you answered {LBL[got]}."))
    t_key, t_you = nj_total(c["nj"]), nj_total(a["nj"])
    ok1 = nj_cat(t_you) == nj_cat(t_key)
    ok2 = a["who"] in c["who"]
    pts += 2 * ok1 + 3 * ok2
    notes.insert(0, (ok1, f"Naranjo score: you {t_you} ({nj_cat(t_you)}), expected {t_key} ({nj_cat(t_key)}). {c['nj_note']}"))
    notes.append((ok2, f"WHO-UMC: accepted {' or '.join(sorted(c['who']))}; you chose {a['who']}. "
                       "Naranjo and WHO-UMC are assessment aids, not mandatory scoring tools."))
    return result(pts, 15, notes)


def grade_expectedness(c, a):
    ok1 = a["exp"] == c["exp"]
    ok2 = a["why"] == c["exp_opts"][c["exp_ok"]]
    return result(10 * ok1 + 5 * ok2, 15, [
        (ok1, f"Expected answer: {c['exp']}."),
        (ok2, f"Reasoning: {c['exp_opts'][c['exp_ok']]}"),
    ])


def due_date(rule_id, dz):
    return dz + dt.timedelta(days=RULE[rule_id]["days"])


def grade_timeline(c, a):
    r = RULE[c["rule"]]
    key_dz = day(c["dz"])
    key_due = due_date(c["rule"], key_dz)
    you_due = due_date(a["rule"], a["dz"])
    ok1, ok2, ok3 = a["rule"] == c["rule"], a["dz"] == key_dz, you_due == key_due
    return result(8 * ok1 + 7 * ok2 + 5 * ok3, 20, [
        (ok1, f"Pathway: {r['name']}, {r['days']} calendar days. These pathways are not interchangeable."),
        (ok2, f"Day Zero: {fmt(key_dz)}. {c['dz_note']}"),
        (ok3, f"Due date: {fmt(key_due)}. Your record gives {fmt(you_due)}."),
    ], critical=not ok1)


WHO_ORD = {"Certain": 4, "Probable/Likely": 3, "Possible": 2, "Unlikely": 1}
NJ_ORD = {"Definite": 4, "Probable": 3, "Possible": 2, "Doubtful": 1}


def qc_checks(c, a, prior):
    """Consistency checks on the learner's own case record."""
    text = a["text"]
    rule = prior["timeline"]["rule"]
    checks = [
        ("Seriousness and reporting pathway are consistent",
         RULE[rule]["serious"] == (prior["seriousness"]["serious"] == "Serious")),
        ("Day Zero is not before the first report was received",
         prior["timeline"]["dz"] >= day(c["received"])),
        ("Naranjo and WHO-UMC conclusions are compatible",
         abs(NJ_ORD[nj_cat(nj_total(prior["causality"]["nj"]))] - WHO_ORD.get(prior["causality"]["who"], 0)) <= 1),
        ("Narrative is at least 60 words", len(text.split()) >= 60),
    ]
    return checks


def grade_narrative(c, a, prior):
    text = a["text"].lower()
    found = [lbl for lbl, kws in c["facts"] if any(k in text for k in kws)]
    missing = [lbl for lbl, _ in c["facts"] if lbl not in found]
    share = len(found) / len(c["facts"])
    checks = qc_checks(c, a, prior)
    pts = 6 * share + sum(ok for _, ok in checks)
    notes = [(not missing, "Narrative key facts found: %d of %d. %s" % (
        len(found), len(c["facts"]), ("Missing: " + "; ".join(missing)) if missing else "Nothing important omitted."))]
    notes += [(ok, "QC: " + label) for label, ok in checks]
    return result(pts, 10, notes)


GRADERS = {
    "validity": grade_validity, "coding": grade_coding, "seriousness": grade_seriousness,
    "causality": grade_causality, "expectedness": grade_expectedness, "timeline": grade_timeline,
}


def grade(stage, case, answer, prior):
    if stage == "narrative":
        return grade_narrative(case, answer, prior)
    return GRADERS[stage](case, answer)


def final_score(grades):
    pts = sum(g["pts"] for g in grades.values())
    mx = sum(g["max"] for g in grades.values())
    raw = round(100 * pts / mx)
    critical = any(g["critical"] for g in grades.values())
    capped = min(raw, CAP) if critical else raw
    return {"raw": raw, "pct": capped, "critical": critical and raw > CAP, "passed": capped >= PASS_MARK}
