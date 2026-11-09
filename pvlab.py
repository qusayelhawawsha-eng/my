"""PV Case Lab - a pharmacovigilance case-processing simulator.
Run with:  streamlit run pvlab.py
All patients, reporters, products and documents are fictional.
"""

import datetime as dt
import json
import time

import pandas as pd
import streamlit as st

from pv_data import (CODING_RULES, CRITERIA, ELEMENTS, EXP_CHOICES, HINTS, NJ_PTS, NJ_Q,
                     PRODUCTS, REFERENCES, RULES, STAGES, WHO_CLASSES, CASES)
from pv_engine import (CASE, PASS_MARK, RULE, day, due_date, final_score, fmt, grade,
                       nj_cat, nj_total, stages_for)

st.set_page_config(page_title="PV Case Lab", page_icon="🧪", layout="wide")
st.markdown(
    "<style>[data-testid='stMetric']{border:1px solid rgba(128,128,128,.3);"
    "border-radius:10px;padding:10px 14px}</style>",
    unsafe_allow_html=True,
)

PAGES = ["Dashboard", "Case inbox", "Case workspace", "Reference library", "My performance"]
S = st.session_state
S.setdefault("page", "Dashboard")
S.setdefault("mode", "Learning")
S.setdefault("history", [])
S.setdefault("active", None)
S.setdefault("n", 0)

WHO_TEXT = {
    "Certain": "Strong evidence and a plausible relationship.",
    "Probable/Likely": "Reasonable timing and alternative causes unlikely.",
    "Possible": "A relationship is plausible, but alternative explanations remain.",
    "Unlikely": "Timing or alternative explanations make causality improbable.",
    "Conditional/Unclassified": "More information is needed.",
    "Unassessable/Unclassifiable": "Information is insufficient or contradictory.",
}


def start(case_id):
    S.n += 1
    S.active = {"case": case_id, "n": S.n, "i": 0, "grades": {}, "ans": {}, "revealed": [],
                "t0": time.time(), "mode": S.mode, "saved": False}
    S.page = "Case workspace"


def go(page):
    S.page = page


def key(att, stage, name):
    return f"a{att['n']}_{stage}_{name}"


def best_scores():
    best = {}
    for h in S.history:
        best[h["case"]] = max(best.get(h["case"], 0), h["pct"])
    return best


# ---------------------------------------------------------------
# Stage screens. Each returns the learner's answer after Submit.
# ---------------------------------------------------------------
def ui_validity(c, att):
    st.write("Check each minimum element against the report.")
    el = {}
    for k, label in ELEMENTS:
        el[k] = st.radio(label, ["Present", "Missing"], horizontal=True, key=key(att, "v", k)) == "Present"
    out = {"el": el}
    out["overall"] = st.radio("Overall assessment", ["Valid ICSR", "Not a valid ICSR (yet)"],
                              index=None, key=key(att, "v", "ov"))
    ready = out["overall"] is not None
    if c["followups"]:
        out["fu"] = st.multiselect(
            "Follow-up questions to send to the reporter (choose up to 3)",
            list(range(len(c["followups"]))), format_func=lambda i: c["followups"][i]["q"],
            max_selections=3, key=key(att, "v", "fu"))
    else:
        out["action"] = st.radio("What do you do with this report?", c["actions"], index=None,
                                 key=key(att, "v", "act"))
        ready = ready and out["action"] is not None
    return out if st.button("Submit", disabled=not ready, key=key(att, "v", "go")) else None


def ui_coding(c, att):
    cd = c["code"]
    st.markdown(f"**Reported (verbatim):** _{cd['verbatim']}_")
    pt = st.radio("Best term from the training dictionary (fictional, not MedDRA)", cd["options"],
                  index=None, key=key(att, "c", "pt"))
    rule = st.radio("Which coding principle applies?", CODING_RULES, index=None, key=key(att, "c", "rule"))
    ready = pt is not None and rule is not None
    return {"pt": pt, "rule": rule} if st.button("Submit", disabled=not ready, key=key(att, "c", "go")) else None


def ui_seriousness(c, att):
    st.write("Select every criterion that applies. Seriousness is not the same as severity.")
    crit = {k for k, label, desc in CRITERIA if st.checkbox(label, help=desc, key=key(att, "s", k))}
    serious = st.radio("Overall", ["Serious", "Non-serious"], index=None, horizontal=True, key=key(att, "s", "ov"))
    return {"crit": crit, "serious": serious} if st.button(
        "Submit", disabled=serious is None, key=key(att, "s", "go")) else None


def ui_causality(c, att):
    st.markdown("**Naranjo scale**")
    letters = {"Yes": "y", "No": "n", "Don't know": "d"}
    nj = [letters[st.radio(f"{i + 1}. {q}", list(letters), index=2, horizontal=True, key=key(att, "n", i))]
          for i, q in enumerate(NJ_Q)]
    total = nj_total(nj)
    st.info(f"Your Naranjo score: {total} ({nj_cat(total)})")
    who = st.selectbox("WHO-UMC category (clinical judgement)", WHO_CLASSES, index=None,
                       placeholder="Choose a category", key=key(att, "n", "who"))
    return {"nj": nj, "who": who} if st.button("Submit", disabled=who is None, key=key(att, "n", "go")) else None


def ui_expectedness(c, att):
    p = PRODUCTS[c["product"]]
    st.markdown(f"**{c['product']} product information** (fictional)  \n"
                f"{p['document']} · version {p['version']} · {p['country']} · effective {p['effective']}")
    st.dataframe(pd.DataFrame(p["reactions"], columns=["Reaction", "Listed frequency"]),
                 hide_index=True, width="stretch")
    st.markdown(f"**Reaction to assess:** {c['exp_event']}")
    exp = st.radio("Your assessment", EXP_CHOICES, index=None, key=key(att, "e", "exp"))
    why = st.radio("Reasoning", c["exp_opts"], index=None, key=key(att, "e", "why"))
    ready = exp is not None and why is not None
    return {"exp": exp, "why": why} if st.button("Submit", disabled=not ready, key=key(att, "e", "go")) else None


def ui_timeline(c, att):
    st.write("Day Zero is the date the minimum criteria are first met, or the date new information changes "
             "the case. Choose the pathway that fits the product, region and your seriousness assessment.")
    rule = st.selectbox("Reporting pathway", [r["id"] for r in RULES], format_func=lambda i: RULE[i]["name"],
                        index=None, placeholder="Choose a pathway", key=key(att, "t", "rule"))
    dz = st.date_input("Day Zero", value=day(c["received"]), min_value=dt.date(2026, 1, 1),
                       max_value=dt.date(2026, 12, 31), key=key(att, "t", "dz"))
    if rule:
        st.info(f"With this pathway and Day Zero, the deadline is {fmt(due_date(rule, dz))} "
                f"({RULE[rule]['days']} calendar days).")
    return {"rule": rule, "dz": dz} if st.button("Submit", disabled=rule is None, key=key(att, "t", "go")) else None


def ui_narrative(c, att):
    st.write("Write the case as a standalone medical story in time order: patient, product and dates, history, "
             "concomitant medicines, onset and course, investigations, treatment, outcome and missing "
             "information. Do not add facts that are not in the case.")
    text = st.text_area("Case narrative", height=220, key=key(att, "r", "text"))
    st.caption("The narrative is checked against a key-facts list by keyword matching, not by AI.")
    done = st.checkbox("I have reviewed my case record before final submission", key=key(att, "r", "qc"))
    ready = done and len(text.strip()) > 0
    return {"text": text} if st.button("Finish case", disabled=not ready, key=key(att, "r", "go")) else None


UI = {"validity": ui_validity, "coding": ui_coding, "seriousness": ui_seriousness,
      "causality": ui_causality, "expectedness": ui_expectedness, "timeline": ui_timeline,
      "narrative": ui_narrative}


# ---------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------
def case_file(c, att):
    with st.container(border=True):
        st.caption(f"{c['id']} · {c['report_type']} · received {fmt(day(c['received']))} · {c['country']} · "
                   f"{c['product']} ({c['status']}) · {c['source']}")
        st.markdown("**Original report**")
        st.write(c["report"])
        for title, text in c.get("docs", []):
            st.markdown(f"**{title}**")
            st.write(text)
        if att["revealed"]:
            st.markdown(f"**Reporter's reply to your follow-up (received {c['reply_date']})**")
            for i in att["revealed"]:
                f = c["followups"][i]
                st.markdown(f"- *{f['q']}*  \n  {f['a']}")


def feedback(g):
    st.metric("Stage score", f"{g['pts']:g} / {g['max']}")
    for ok, text in g["notes"]:
        st.markdown(f"{'✅' if ok else '❌'} {text}")


def stage_panel(c, att, stage):
    skey, label, mx = stage
    st.subheader(f"{label} ({mx} points)")
    if skey in att["grades"]:
        feedback(att["grades"][skey])
        if st.button("Continue", key=key(att, skey, "next")):
            att["i"] += 1
            st.rerun()
        return
    if att["mode"] == "Learning":
        with st.expander("Hint"):
            st.write(HINTS[skey])
    ans = UI[skey](c, att)
    if ans is not None:
        att["ans"][skey] = ans
        att["grades"][skey] = grade(skey, c, ans, att["ans"])
        if skey == "validity":
            needed = {i for i, f in enumerate(c["followups"]) if f.get("needed")}
            att["revealed"] = sorted(set(ans.get("fu", [])) | needed)
        if att["mode"] == "Assessment":
            att["i"] += 1
        st.rerun()


def report(c, att):
    s = final_score(att["grades"])
    if not att["saved"]:
        S.history.append({"case": c["id"], "pct": s["pct"], "raw": s["raw"], "passed": s["passed"],
                          "minutes": round((time.time() - att["t0"]) / 60, 1),
                          "stages": {k: round(100 * g["pts"] / g["max"]) for k, g in att["grades"].items()},
                          "date": dt.date.today().isoformat()})
        att["saved"] = True
    st.subheader("Case result")
    a, b = st.columns(2)
    a.metric("Score", f"{s['pct']} / 100")
    b.metric("Result", "Passed" if s["passed"] else "Not passed", f"pass mark {PASS_MARK}", delta_color="off")
    if s["critical"]:
        st.error(f"Critical error: the seriousness decision or the reporting pathway was wrong. Your raw score "
                 f"was {s['raw']}, but a wrong regulatory decision caps the score below the pass mark. "
                 "Retry the case.")
    rows = [{"Area": label, "Points": att["grades"][k]["pts"], "Out of": mx}
            for k, label, mx in stages_for(c) if k in att["grades"]]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    for k, label, mx in stages_for(c):
        with st.expander(f"{label}: explanations"):
            feedback(att["grades"][k])
    x, y = st.columns(2)
    x.button("Retry this case", on_click=start, args=(c["id"],), width="stretch")
    y.button("Back to the case inbox", on_click=go, args=("Case inbox",), width="stretch")


def page_workspace():
    att = S.active
    if not att:
        st.info("No case is open. Choose one in the Case inbox.")
        st.button("Go to the case inbox", on_click=go, args=("Case inbox",))
        return
    c = CASE[att["case"]]
    stages = stages_for(c)
    st.title(f"{c['id']} · {c['title']}")
    st.caption(f"Mode: {att['mode']}")
    left, mid, right = st.columns([1.1, 3.4, 1.5])
    with left:
        st.markdown("**Workflow**")
        for idx, (k, label, _) in enumerate(stages):
            icon = "✅" if k in att["grades"] else "▶️" if idx == att["i"] else "⚪"
            st.markdown(f"{icon} {idx + 1}. {label}")
    with mid:
        case_file(c, att)
        if att["i"] >= len(stages):
            report(c, att)
        else:
            stage_panel(c, att, stages[att["i"]])
    with right:
        st.markdown("**Case summary**")
        for k, label, _ in stages:
            if k in att["grades"]:
                g = att["grades"][k]
                st.write(f"{label}: " + (f"{g['pts']:g}/{g['max']}" if att["mode"] == "Learning" else "recorded"))
            else:
                st.write(f"{label}: pending")
        t = att["ans"].get("timeline")
        if t and t["rule"]:
            st.divider()
            st.write(f"Day Zero: {fmt(t['dz'])}")
            st.write(f"Deadline: {fmt(due_date(t['rule'], t['dz']))}")


# ---------------------------------------------------------------
# Other pages
# ---------------------------------------------------------------
def page_dashboard():
    st.title("PV Case Lab")
    st.caption("Learn pharmacovigilance by processing realistic cases, not by memorising definitions.")
    h = S.history
    a, b, c_, d = st.columns(4)
    a.metric("Cases attempted", len(h))
    b.metric("Cases passed", len({x["case"] for x in h if x["passed"]}))
    c_.metric("Average score", f"{round(sum(x['pct'] for x in h) / len(h))}%" if h else "-")
    d.metric("Average time", f"{round(sum(x['minutes'] for x in h) / len(h), 1)} min" if h else "-")
    if not h:
        st.info("Start with PV-001. You will receive a report, process it step by step and get a "
                "scored case record with explanations.")
        st.button("Start PV-001", on_click=start, args=("PV-001",))
    else:
        totals = {}
        for x in h:
            for k, v in x["stages"].items():
                totals.setdefault(k, []).append(v)
        names = {k: label for k, label, _ in STAGES}
        weak = min(totals, key=lambda k: sum(totals[k]) / len(totals[k]))
        st.warning(f"Your weakest area so far: {names[weak]} ({round(sum(totals[weak]) / len(totals[weak]))}% average).")
        best = best_scores()
        todo = [x for x in CASES if best.get(x["id"], 0) < PASS_MARK]
        if todo:
            nxt = todo[0]
            st.write(f"Recommended next case: **{nxt['id']} · {nxt['title']}**")
            st.button("Open it", on_click=start, args=(nxt["id"],))
        else:
            st.success("You passed every available case. Add more cases in pv_data.py.")
    with st.expander("Save or load your progress"):
        st.write("Progress lives only in this browser session. Download it to keep it, and load it next time.")
        st.download_button("Download my progress", json.dumps(S.history), file_name="pv_case_lab_progress.json")
        up = st.file_uploader("Load a saved progress file", type="json")
        if up is not None and st.button("Load this file"):
            try:
                data = json.load(up)
                assert isinstance(data, list) and all("case" in x and "pct" in x for x in data)
                S.history = data
                st.rerun()
            except Exception:
                st.error("This file is not a valid progress file.")


def page_inbox():
    st.title("Case inbox")
    best = best_scores()
    for c in CASES:
        with st.container(border=True):
            left, right = st.columns([5, 1.2])
            left.markdown(f"**{c['id']} · {c['title']}**")
            status = f"best score {best[c['id']]}" if c["id"] in best else "new"
            left.caption(f"{c['level']} · {c['source']} · received {fmt(day(c['received']))} · "
                         f"{c['product']} · {status}")
            right.button("Retry" if c["id"] in best else "Start", key=f"start_{c['id']}",
                         on_click=start, args=(c["id"],), width="stretch")


def page_reference():
    st.title("Reference library")
    st.warning("Training content for learning only. Rules change. Always check the current official guidance "
               "before relying on any rule. The rule set here has not been reviewed by an independent "
               "pharmacovigilance professional.")
    t1, t2, t3, t4, t5 = st.tabs(["Reporting rules", "Naranjo", "WHO-UMC", "Seriousness", "Sources"])
    with t1:
        st.write("Version 1 covers the EU post-marketing pathway completely. The other rows show that "
                 "different pathways are not interchangeable. In the EU, serious ICSRs have a 15-day "
                 "requirement including serious expected cases, while the US 15-day alert is for serious "
                 "and unexpected experiences.")
        st.dataframe(pd.DataFrame([{"Pathway": r["name"], "Calendar days": r["days"], "Framework": r["framework"],
                                    "Source": r["source"], "Rule version": r["version"]} for r in RULES]),
                     hide_index=True, width="stretch")
    with t2:
        st.dataframe(pd.DataFrame([{"Question": q, "Yes": NJ_PTS[i][0], "No": NJ_PTS[i][1], "Don't know": 0}
                                   for i, q in enumerate(NJ_Q)]), hide_index=True, width="stretch")
        st.write("Total: 9 or more Definite, 5 to 8 Probable, 1 to 4 Possible, 0 or less Doubtful. "
                 "It is an assessment aid, not a mandatory regulatory tool.")
    with t3:
        st.dataframe(pd.DataFrame([{"Category": k, "Meaning": v} for k, v in WHO_TEXT.items()]),
                     hide_index=True, width="stretch")
    with t4:
        st.dataframe(pd.DataFrame([{"Criterion": l, "Question": d} for _, l, d in CRITERIA]),
                     hide_index=True, width="stretch")
        st.write("Seriousness is not severity. A severe headache may be non-serious; a moderate event "
                 "needing hospital admission is serious.")
    with t5:
        st.dataframe(pd.DataFrame(REFERENCES, columns=["Reference", "Used for", "Where"]),
                     hide_index=True, width="stretch")


def page_performance():
    st.title("My performance")
    if not S.history:
        st.info("No attempts yet.")
        return
    h = pd.DataFrame(S.history)
    st.line_chart(h["pct"], y_label="Score")
    names = {k: label for k, label, _ in STAGES}
    avg = {}
    for x in S.history:
        for k, v in x["stages"].items():
            avg.setdefault(names[k], []).append(v)
    st.bar_chart(pd.Series({k: sum(v) / len(v) for k, v in avg.items()}), y_label="Average %")
    st.dataframe(h[["date", "case", "pct", "raw", "passed", "minutes"]], hide_index=True, width="stretch")


# ---------------------------------------------------------------
# Sidebar and routing
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧪 PV Case Lab")
    st.radio("Menu", PAGES, key="page")
    st.radio("Mode", ["Learning", "Assessment"], key="mode",
             help="Learning: hints and feedback after each stage. Assessment: no hints, results at the end. "
                  "The mode applies to the next case you start.")
    st.caption("Training simulator with fictional data. Not a validated pharmacovigilance system and "
               "not a regulatory submission tool. Never enter real patient data.")

{"Dashboard": page_dashboard, "Case inbox": page_inbox, "Case workspace": page_workspace,
 "Reference library": page_reference, "My performance": page_performance}[S.page]()
